# src/models/LugaresModel.py
"""Lugares Model using native SQLAlchemy 2.0"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.orm import Session

from . import Base


class LugaresModel(Base):
    """
    Lugares (Locations/Places) Model
    Table: invLugares
    """
    
    __tablename__ = 'invLugares'

    id = Column(Integer, primary_key=True, index=True)
    lugar = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, lugar: str, activo: bool = True):
        """Initialize a new Lugar"""
        self.lugar = lugar
        self.activo = activo
        self.fechaAlta = datetime.utcnow()
        self.fechaUltimaModificacion = datetime.utcnow()

    @staticmethod
    def get_all_lugares(db: Session):
        """Get all locations"""
        query = select(LugaresModel)
        return db.execute(query).scalars().all()

    @staticmethod
    def get_one_lugar(db: Session, id: int):
        """Get a single location by ID"""
        query = select(LugaresModel).where(LugaresModel.id == id)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_lugar_by_nombre(db: Session, value: str):
        """Get location by name"""
        query = select(LugaresModel).where(LugaresModel.lugar == value)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_lugar_by_like(db: Session, value: str, offset: int = 0, limit: int = 10):
        """Search locations by name pattern"""
        query = (
            select(LugaresModel)
            .where(LugaresModel.lugar.ilike(f'%{value}%'))
            .order_by(LugaresModel.id)
            .offset(offset)
            .limit(limit)
        )
        return db.execute(query).scalars().all()

    @staticmethod
    def create_lugar(db: Session, lugar: str, activo: bool = True) -> 'LugaresModel':
        """Create a new location"""
        new_lugar = LugaresModel(lugar=lugar, activo=activo)
        db.add(new_lugar)
        db.commit()
        db.refresh(new_lugar)
        return new_lugar

    def update(self, db: Session, **kwargs):
        """Update location fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.fechaUltimaModificacion = datetime.utcnow()
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        """Delete location"""
        db.delete(self)
        db.commit()

    def __repr__(self):
        return f'<Lugar {self.id}: {self.lugar}>'