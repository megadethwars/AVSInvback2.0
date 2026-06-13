"""
SQLAlchemy database configuration for FastAPI
Using native SQLAlchemy 2.0 without Flask dependency
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

# Database URI - configure from environment or hardcoded for now
DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "mssql+pymssql://forrerunner97:Asterisco97@inventarioavs1.database.windows.net/avsInventory"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Test connections before using
    echo=False,  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency injection for FastAPI to get database session.
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this once when the application starts.
    """
    Base.metadata.create_all(bind=engine)
