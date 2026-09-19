import os
import shutil
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger("flash_flood_db")

def get_sqlite_url() -> str:
    """
    Returns a valid SQLite URL. If running in a serverless environment (e.g., Vercel / AWS Lambda),
    uses /tmp directory to avoid read-only filesystem errors.
    """
    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("LAMBDA_TASK_ROOT"))
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    bundled_db = os.path.join(base_dir, 'flash_flood.db')
    
    if is_serverless:
        tmp_db = "/tmp/flash_flood.db"
        if not os.path.exists(tmp_db) and os.path.exists(bundled_db):
            try:
                shutil.copyfile(bundled_db, tmp_db)
            except Exception as e:
                logger.warning(f"Could not copy bundled SQLite database to /tmp: {e}")
        return f"sqlite:///{tmp_db}"
    else:
        sqlite_path = bundled_db.replace('\\', '/')
        return f"sqlite:///{sqlite_path}"

def create_resilient_engine():
    raw_url = (settings.DATABASE_URL or "").strip()
    
    # 1. Normalize empty or placeholder strings to SQLite
    if not raw_url or raw_url.lower() in ('""', "''", "none", "null", "false"):
        sqlite_url = get_sqlite_url()
        return create_engine(sqlite_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
    
    # 2. Fix postgres:// legacy dialect prefix for SQLAlchemy 2.0+
    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    
    # 3. Direct SQLite connection
    if raw_url.startswith("sqlite"):
        if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            raw_url = get_sqlite_url()
        connect_args = {"check_same_thread": False}
        return create_engine(raw_url, connect_args=connect_args, pool_pre_ping=True)
    
    # 4. Attempt PostgreSQL / External database connection
    try:
        pg_engine = create_engine(raw_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to PostgreSQL database.")
        return pg_engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database.")
        sqlite_url = get_sqlite_url()
        return create_engine(sqlite_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)

engine = create_resilient_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
