#src/models/__init__.py
"""Models package - uses native SQLAlchemy (no Flask dependency)"""

from ..database import Base, SessionLocal, engine

# Re-export for backwards compatibility with old imports
__all__ = ["Base", "SessionLocal", "engine"]