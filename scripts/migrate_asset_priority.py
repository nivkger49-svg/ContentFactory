from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "factory.sqlite"
SCHEMA_PATH = ROOT / "db" / "schema.sql"


def main() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8-sig")
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)
    print(f"Asset priority tables ready: {DB_PATH}")


if __name__ == "__main__":
    main()
