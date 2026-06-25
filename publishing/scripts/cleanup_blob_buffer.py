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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = load_config()
    worker = PublishWorker(config)
    payload = {
        "buffer_status": worker.blob_buffer.get_status(),
        "cleanup_result": worker.cleanup_blob_buffer(force=args.force),
        "buffer_status_after": worker.blob_buffer.get_status(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
