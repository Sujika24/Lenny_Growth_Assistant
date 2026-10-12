import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    """
    Attempts to initialize the PostgreSQL engine.
    If PostgreSQL is unreachable or fails to connect, gracefully falls back to SQLite.
    """
    engine = None
    if settings.database_url:
        try:
            candidate_engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 3} if "psycopg" in settings.database_url else {}
            )
            # Test connection
            with candidate_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Connected successfully to PostgreSQL database.")
            return candidate_engine
        except Exception as e:
            logger.warning(
                f"PostgreSQL connection to '{settings.database_url}' failed: {e}. "
                f"Falling back to local SQLite: {settings.sqlite_fallback_url}"
            )

    # SQLite fallback
    fallback_engine = create_engine(
        settings.sqlite_fallback_url,
        connect_args={"check_same_thread": False}
    )
    logger.info(f"Using SQLite database engine at {settings.sqlite_fallback_url}")
    return fallback_engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import SessionModel, MessageModel, ArtifactModel # noqa
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")
