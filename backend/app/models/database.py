import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rfq_system.db")

# Create engine with SQLite-specific settings
engine: Engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)
