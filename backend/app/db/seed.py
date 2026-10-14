"""Apply seed_data.sql. Run AFTER migrations:  python -m app.db.seed [--force]

By default seeding is skipped when the doctors table already has rows, so it is safe to re-run.
"""
import sys
from pathlib import Path

from sqlalchemy import text

from app.core.config import BACKEND_DIR
from app.db.session import engine

SEED_FILE = BACKEND_DIR / "seed_data.sql"


def seed(target_engine=engine, path: Path = SEED_FILE, force: bool = False) -> bool:
    with target_engine.connect() as conn:
        existing = conn.execute(text("SELECT COUNT(*) FROM doctors")).scalar_one()
    if existing and not force:
        return False
    raw = target_engine.raw_connection()
    try:
        raw.executescript(path.read_text(encoding="utf-8"))
        raw.commit()
    finally:
        raw.close()
    return True


if __name__ == "__main__":
    applied = seed(force="--force" in sys.argv)
    print("Seed data applied." if applied else "Doctors already exist - seeding skipped (use --force to re-apply).")
