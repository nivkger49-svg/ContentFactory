from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from config import load_config
from publish_worker import PublishWorker


def _json_default(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["draft", "schedule", "publish"])
    args = parser.parse_args()

    config = load_config()
    if args.mode:
        object.__setattr__(config, "publish_mode", args.mode)

    worker = PublishWorker(config)
    worker.scan_and_queue()
    result = worker.schedule_all()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
