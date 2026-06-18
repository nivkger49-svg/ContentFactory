from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "factory.sqlite"
SCHEMA_PATH = ROOT / "db" / "schema.sql"


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8-sig")
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)
        conn.execute(
            "INSERT OR IGNORE INTO assets(path, asset_type, source, license_status, notes) VALUES (?, ?, ?, ?, ?)",
            ("assets/raw", "folder", "local", "mixed", "Drop user-provided raw source material here."),
        )
    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
