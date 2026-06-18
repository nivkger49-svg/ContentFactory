from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "factory.sqlite"


def main():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, status, platform, topic, hook, created_at
            FROM videos
            ORDER BY id DESC
            LIMIT 25
            """
        ).fetchall()

    if not rows:
        print("No video ideas yet.")
        return

    for row in rows:
        print(f"#{row['id']} [{row['status']}] {row['title']}")
        if row["topic"]:
            print(f"  topic: {row['topic']}")
        if row["hook"]:
            print(f"  hook: {row['hook']}")


if __name__ == "__main__":
    main()
