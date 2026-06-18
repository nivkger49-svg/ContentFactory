from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "factory.sqlite"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_idea.py \"Video title\" [topic] [hook]")
        raise SystemExit(2)

    title = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else None
    hook = sys.argv[3] if len(sys.argv) > 3 else None

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO videos(title, topic, hook, status) VALUES (?, ?, ?, 'idea')",
            (title, topic, hook),
        )
        video_id = cur.lastrowid
    print(f"Added idea #{video_id}: {title}")


if __name__ == "__main__":
    main()
