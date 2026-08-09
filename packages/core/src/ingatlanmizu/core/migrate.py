from pathlib import Path
import psycopg
from ingatlanmizu.core.config import settings

MIGRATIONS = Path(__file__).resolve().parents[5] / "db" / "migrations"

TRACKING = """
CREATE SCHEMA IF NOT EXISTS ops;
CREATE TABLE IF NOT EXISTS ops.schema_migrations (
    filename    text PRIMARY KEY,
    applied_at  timestamptz NOT NULL DEFAULT now()
);
"""

def main() -> None:
    with psycopg.connect(settings.database_url, autocommit=False) as conn:
        conn.execute(TRACKING)
        conn.commit()
        applied = {r[0] for r in conn.execute(
            "SELECT filename FROM ops.schema_migrations")}

        for path in sorted(MIGRATIONS.glob("*.sql")):
            if path.name in applied:
                continue
            print(f"applying {path.name}")
            conn.execute(path.read_text())
            conn.execute(
                "INSERT INTO ops.schema_migrations (filename) VALUES (%s)",
                (path.name,))
            conn.commit()
    print("up to date")