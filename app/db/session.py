import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger("flash_flood_db")

def create_resilient_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        return create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
    
    # Try connecting to PostgreSQL
    try:
        pg_engine = create_engine(db_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to PostgreSQL database.")
        return pg_engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database.")
        sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'flash_flood.db')).replace('\\', '/')
        sqlite_url = f"sqlite:///{sqlite_path}"
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
