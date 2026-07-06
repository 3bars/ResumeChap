"""Database setup for ResumeChap.

Uses SQLite so the app is fully self-hosted with zero external services.
The database file lives in a per-user data directory so it persists across
runs and survives app upgrades.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _data_dir() -> Path:
    """Return a writable per-user data directory (cross-platform)."""
    # Allow override for advanced users / packaging.
    override = os.environ.get("RESUMECHAP_DATA_DIR")
    if override:
        base = Path(override)
    elif os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home())) / "ResumeChap"
    else:  # macOS / Linux
        base = Path.home() / ".resumechap"
    base.mkdir(parents=True, exist_ok=True)
    return base


DATA_DIR = _data_dir()
DB_PATH = DATA_DIR / "resumechap.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
