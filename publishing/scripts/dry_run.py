from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from config import load_config
from publish_worker import PublishWorker


def main() -> None:
    config = load_config()
    worker = PublishWorker(config)
    worker.scan_and_queue()
    scheduled = worker.plan_schedule()

    payload = {
        "mode": config.publish_mode,
        "queue_length": len(worker.queue),
        "scheduled_preview": scheduled,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
