"""
SQLAlchemy engine + session factory.

Works against any Postgres URL — local Postgres or Supabase's connection
string both work fine, nothing here is Supabase-specific.
"""
try:
    from sqlalchemy import create_engine # pyright: ignore[reportMissingImports]
    from sqlalchemy.orm import sessionmaker, declarative_base # pyright: ignore[reportMissingImports]
except ImportError as exc:
    raise ImportError(
        "SQLAlchemy is required to create the database session. "
        "Install it with `pip install SQLAlchemy`."
    ) from exc

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a session, always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()