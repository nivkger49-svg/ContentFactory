from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "factory.sqlite"
LOOKBACK_BATCHES = 3
MIN_PICK_SCORE = 3.0
STALE_THRESHOLD = 4.0


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rel_path(path: str | Path) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.resolve().relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            return str(p).replace("\\", "/")
    return str(p).replace("\\", "/")


def batch_number(batch_id: str) -> int | None:
    match = re.search(r"(\d+)$", batch_id or "")
    return int(match.group(1)) if match else None


def tokenize(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[\wа-яА-ЯіІїЇєЄґҐ]+", text or "", flags=re.UNICODE)}


def asset_exists(path_text: str) -> bool:
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path_text
    return path.exists()


def scene_overlap_score(scene: sqlite3.Row, role: str, themes: set[str]) -> tuple[float, list[str]]:
    fit = float(scene["score"] or 0)
    reasons = [f"base_scene_score={fit:g}"]
    role_text = (scene["role"] or "").lower()
    if role and role.lower() in role_text:
        fit += 1.0
        reasons.append("role_match=+1.0")
    elif role:
        fit -= 1.5
        reasons.append("role_mismatch=-1.5")
    scene_tokens = tokenize(" ".join(str(scene[k] or "") for k in ("themes", "visual", "emotion", "comment")))
    hits = sorted(themes & scene_tokens)
    if hits:
        boost = min(1.0, 0.25 * len(hits))
        fit += boost
        reasons.append(f"theme_hits={','.join(hits[:6])}=+{boost:g}")
    asset_type = (scene["asset_type"] or "").lower()
    if role in {"product", "product moment"} and asset_type == "site_master_recording":
        fit += 0.5
        reasons.append("site_product_boost=+0.5")
    if role == "cta" and asset_type == "generated_image":
        fit += 0.5
        reasons.append("cta_bg_boost=+0.5")
    return max(0.0, min(6.5, fit)), reasons


def recent_usage(conn: sqlite3.Connection, asset_id: int, current_batch: str) -> tuple[float, float, str | None, list[str]]:
    rows = conn.execute(
        """
        SELECT batch_id, variant, used_at
        FROM batch_asset_usage
        WHERE asset_id = ?
        ORDER BY used_at DESC, id DESC
        """,
        (asset_id,),
    ).fetchall()
    if not rows:
        return 0.0, 1.0, None, ["fresh_asset=+1.0"]

    current_n = batch_number(current_batch)
    penalty = 0.0
    last_batch = rows[0]["batch_id"]
    reasons: list[str] = []
    for row in rows:
        used_batch = row["batch_id"]
        if used_batch == current_batch:
            penalty = max(penalty, 3.0)
            reasons.append("used_current_batch=-3.0")
            continue
        if current_n is not None:
            used_n = batch_number(used_batch)
            if used_n is not None:
                delta = current_n - used_n
                if delta == 1:
                    penalty = max(penalty, 2.0)
                    reasons.append(f"used_previous_batch={used_batch}=-2.0")
                elif delta == 2:
                    penalty = max(penalty, 1.0)
                    reasons.append(f"used_2_batches_ago={used_batch}=-1.0")
    variety_bonus = 0.0 if penalty else 1.0
    if variety_bonus:
        reasons.append("outside_lookback=+1.0")
    return penalty, variety_bonus, last_batch, reasons


def rank_assets(args: argparse.Namespace) -> dict[str, Any]:
    role = args.role.strip().lower()
    themes = tokenize(args.themes.replace(",", " "))
    limit = int(args.limit)
    with connect() as conn:
        reject_ids = {
            int(row["asset_id"])
            for row in conn.execute(
                "SELECT asset_id FROM asset_tags WHERE lower(tag_value) = 'reject_ua'"
            )
        }
        scenes = conn.execute(
            """
            SELECT
              s.id AS scene_id, s.asset_id, s.start_time, s.end_time, s.visual, s.emotion,
              s.themes, s.role, s.score, s.comment, a.path, a.asset_type, a.source, a.notes
            FROM asset_scenes s
            JOIN assets a ON a.id = s.asset_id
            WHERE COALESCE(s.score, 0) > 1
            """
        ).fetchall()

        best_by_asset: dict[int, dict[str, Any]] = {}
        for scene in scenes:
            asset_id = int(scene["asset_id"])
            if asset_id in reject_ids:
                continue
            if not asset_exists(scene["path"]):
                continue
            haystack = tokenize(" ".join(str(scene[k] or "") for k in ("role", "themes", "visual", "emotion", "comment")))
            if role and role not in haystack and not (themes & haystack):
                continue
            fit, fit_reasons = scene_overlap_score(scene, role, themes)
            penalty, variety, last_batch, usage_reasons = recent_usage(conn, asset_id, args.batch)
            priority = max(0.0, min(10.0, fit + variety - penalty))
            item = {
                "asset_id": asset_id,
                "path": scene["path"],
                "asset_type": scene["asset_type"],
                "source": scene["source"],
                "scene_id": int(scene["scene_id"]),
                "scene_role": scene["role"],
                "visual": scene["visual"],
                "emotion": scene["emotion"],
                "themes": scene["themes"],
                "fit_score": round(fit, 2),
                "repeat_penalty": round(penalty, 2),
                "variety_bonus": round(variety, 2),
                "priority_score": round(priority, 2),
                "last_used_batch": last_batch,
                "reason": "; ".join(fit_reasons + usage_reasons),
            }
            if asset_id not in best_by_asset or item["priority_score"] > best_by_asset[asset_id]["priority_score"]:
                best_by_asset[asset_id] = item

        candidates = sorted(
            best_by_asset.values(),
            key=lambda x: (x["priority_score"], x["fit_score"], x["variety_bonus"]),
            reverse=True,
        )[:limit]

    best = candidates[0]["priority_score"] if candidates else 0.0
    decision = "gap"
    if best >= STALE_THRESHOLD:
        decision = "pick_local"
    elif best >= MIN_PICK_SCORE:
        decision = "stale"

    return {
        "batch": args.batch,
        "scene_role": role,
        "themes": sorted(themes),
        "decision": decision,
        "pexels_recommended": decision in {"gap", "stale"},
        "pexels_query_hint": query_hint(role, themes),
        "candidates": candidates,
    }


def query_hint(role: str, themes: set[str]) -> str:
    base = " ".join(sorted(themes))
    if role == "hook":
        return f"european woman phone reaction {base} portrait".strip()
    if "money" in themes or "finance" in themes:
        return "european woman financial planning calculator portrait"
    if "instagram" in themes or "scroll" in themes:
        return "european woman scrolling phone social media portrait"
    return f"european woman {base} portrait".strip()


def load_storyboard(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def record_storyboard(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.storyboard).resolve()
    data = load_storyboard(path)
    batch = args.batch or data.get("batch") or path.parent.name
    variant = args.variant or data.get("variant") or path.stem
    draft_path = data.get("draft") or data.get("draft_path")
    rows = 0
    skipped = 0
    with connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        for idx, scene in enumerate(data.get("scenes", [])):
            asset_id = scene.get("asset_id")
            if asset_id is None:
                skipped += 1
                continue
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO batch_asset_usage(
                  batch_id, variant, asset_id, scene_role, scene_index, storyboard_path, draft_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (batch, variant, int(asset_id), scene.get("role"), idx, rel_path(path), draft_path),
            )
            rows += max(0, cursor.rowcount)
        conn.commit()
    return {"storyboard": str(path), "batch": batch, "variant": variant, "scenes_seen": len(data.get("scenes", [])), "skipped": skipped, "attempted": rows}


def backfill_usage(args: argparse.Namespace) -> dict[str, Any]:
    base = Path(args.batches_dir).resolve()
    files = sorted(base.rglob("storyboard*.json"))
    results = []
    total = 0
    for file in files:
        ns = argparse.Namespace(storyboard=str(file), batch=None, variant=None)
        result = record_storyboard(ns)
        results.append(result)
        total += result["attempted"]
    return {"files_seen": len(files), "attempted_inserts": total, "results": results}


def plan(args: argparse.Namespace) -> dict[str, Any]:
    brief_path = Path(args.brief).resolve()
    data = load_storyboard(brief_path)
    scenes = []
    for scene in data.get("scenes", []):
        role = scene.get("role", "")
        themes = scene.get("themes") or scene.get("theme") or scene.get("brief") or scene.get("note") or ""
        ns = argparse.Namespace(role=role, themes=str(themes), batch=args.batch, limit=args.limit)
        scenes.append({"scene": scene, "ranking": rank_assets(ns)})
    result = {"batch": args.batch, "brief": str(brief_path), "scenes": scenes}
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank, plan, and record asset usage for ContentFactory.")
    sub = parser.add_subparsers(dest="command", required=True)

    rank_p = sub.add_parser("rank")
    rank_p.add_argument("--role", required=True)
    rank_p.add_argument("--themes", default="")
    rank_p.add_argument("--batch", required=True)
    rank_p.add_argument("--limit", type=int, default=10)
    rank_p.set_defaults(func=rank_assets)

    plan_p = sub.add_parser("plan")
    plan_p.add_argument("--brief", required=True)
    plan_p.add_argument("--batch", required=True)
    plan_p.add_argument("--limit", type=int, default=8)
    plan_p.add_argument("--out")
    plan_p.set_defaults(func=plan)

    record_p = sub.add_parser("record")
    record_p.add_argument("--storyboard", required=True)
    record_p.add_argument("--batch")
    record_p.add_argument("--variant")
    record_p.set_defaults(func=record_storyboard)

    backfill_p = sub.add_parser("backfill-usage")
    backfill_p.add_argument("--batches-dir", default=str(ROOT / "batches"))
    backfill_p.set_defaults(func=backfill_usage)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
