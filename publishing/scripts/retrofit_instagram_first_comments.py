from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from config import load_config
from pinned_comment import build_planned_comment_text
from zernio_client import ZernioClient


def main() -> None:
    cfg = load_config()
    state = json.loads(cfg.state_file.read_text(encoding="utf-8"))
    client = ZernioClient(cfg)
    sdk = client._sdk()
    instagram_account = next(
        platform
        for platform in client.get_target_platforms()
        if platform["platform"] == "instagram"
    )

    now = datetime.now(timezone.utc)
    results: list[dict[str, str]] = []

    for file_name, record in state.items():
        post_id = str(record.get("zernio_post_id") or "").strip()
        scheduled_for = str(record.get("scheduled_for") or "").strip()
        if not post_id or not scheduled_for:
            continue

        try:
            scheduled_at = datetime.fromisoformat(scheduled_for.replace("Z", "+00:00"))
        except ValueError:
            results.append(
                {
                    "file": file_name,
                    "post_id": post_id,
                    "result": "skipped_bad_date",
                    "scheduled_for": scheduled_for,
                }
            )
            continue

        if scheduled_at <= now:
            results.append(
                {
                    "file": file_name,
                    "post_id": post_id,
                    "result": "skipped_not_future",
                    "scheduled_for": scheduled_for,
                }
            )
            continue

        first_comment = build_planned_comment_text(
            config=cfg,
            video_id=file_name,
            platform="instagram",
            reference_at=scheduled_for,
        )

        sdk.posts.update(
            post_id,
            platforms=[
                {
                    "platform": "instagram",
                    "accountId": instagram_account["accountId"],
                    "platformSpecificData": {
                        "firstComment": first_comment,
                    },
                }
            ],
        )

        record["instagram_first_comment"] = first_comment
        record["instagram_first_comment_reference_at"] = scheduled_for
        results.append(
            {
                "file": file_name,
                "post_id": post_id,
                "result": "updated",
                "scheduled_for": scheduled_for,
            }
        )

    cfg.state_file.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
