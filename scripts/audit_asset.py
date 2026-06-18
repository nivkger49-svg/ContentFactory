from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "factory.sqlite"


def resolve_asset_id(conn: sqlite3.Connection, asset: str) -> tuple[int, str]:
    if asset.isdigit():
        row = conn.execute("SELECT id, path FROM assets WHERE id = ?", (int(asset),)).fetchone()
    else:
        candidate = Path(asset)
        path_text = str(candidate).replace("\\", "/")
        if candidate.is_absolute():
            try:
                path_text = str(candidate.resolve().relative_to(ROOT)).replace("\\", "/")
            except ValueError:
                path_text = str(candidate.resolve()).replace("\\", "/")
        row = conn.execute("SELECT id, path FROM assets WHERE path = ?", (path_text,)).fetchone()
    if row is None:
        raise SystemExit(f"Asset not found: {asset}. Run intake_assets.py first.")
    return int(row[0]), str(row[1])


def add_scene(args: argparse.Namespace) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        asset_id, asset_path = resolve_asset_id(conn, args.asset)
        cur = conn.execute(
            """
            INSERT INTO asset_scenes(asset_id, start_time, end_time, role, visual, emotion, themes, score, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                args.start,
                args.end,
                args.role,
                args.visual,
                args.emotion,
                args.themes,
                args.score,
                args.comment,
            ),
        )
        scene_id = cur.lastrowid
        conn.commit()
    return {"scene_id": scene_id, "asset_id": asset_id, "path": asset_path}


def list_asset(args: argparse.Namespace) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        asset_id, asset_path = resolve_asset_id(conn, args.asset)
        conn.row_factory = sqlite3.Row
        scenes = conn.execute(
            """
            SELECT id, start_time, end_time, role, visual, emotion, themes, score, comment, created_at
            FROM asset_scenes
            WHERE asset_id = ?
            ORDER BY start_time, id
            """,
            (asset_id,),
        ).fetchall()
    return {
        "asset_id": asset_id,
        "path": asset_path,
        "scenes": [dict(row) for row in scenes],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add or inspect manual scene audit rows for an asset.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add one scene audit row for an asset.")
    add_p.add_argument("--asset", required=True, help="Asset id or repo-relative path.")
    add_p.add_argument("--start", type=float, default=0.0)
    add_p.add_argument("--end", type=float, default=None)
    add_p.add_argument("--role", required=True, help="hook, bridge, product, cta, etc.")
    add_p.add_argument("--visual", required=True)
    add_p.add_argument("--emotion", default="")
    add_p.add_argument("--themes", default="")
    add_p.add_argument("--score", type=float, default=3.0)
    add_p.add_argument("--comment", default="")
    add_p.set_defaults(func=add_scene)

    list_p = sub.add_parser("list", help="List scene audit rows for one asset.")
    list_p.add_argument("--asset", required=True, help="Asset id or repo-relative path.")
    list_p.set_defaults(func=list_asset)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
