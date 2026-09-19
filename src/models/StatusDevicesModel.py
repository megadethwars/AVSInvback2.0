"""StatusDevices Model using native SQLAlchemy 2.0"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, select
from sqlalchemy.orm import Session

from . import Base


class StatusDevicesModel(Base):
    """
    Status Devices Model
    Table: invStatusDevices
    """
    
    __tablename__ = 'invStatusDevices'

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(100), nullable=False)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, descripcion: str):
        """
        Initialize a new Status Device
        """
        self.descripcion = descripcion
        self.fechaAlta = datetime.utcnow()
        self.fechaUltimaModificacion = datetime.utcnow()

    @staticmethod
    def get_all_status(db: Session):
        """Get all status"""
        query = select(StatusDevicesModel)
        return db.execute(query).scalars().all()

    @staticmethod
    def get_one_status(db: Session, id: int):
        """Get a single status by ID"""
        query = select(StatusDevicesModel).where(StatusDevicesModel.id == id)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_status_by_nombre(db: Session, value: str):
        """Get status by name"""
        query = select(StatusDevicesModel).where(StatusDevicesModel.descripcion == value)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def create_status(db: Session, descripcion: str) -> 'StatusDevicesModel':
        """Create a new status"""
        new_status = StatusDevicesModel(descripcion=descripcion)
        db.add(new_status)
        db.commit()
        db.refresh(new_status)
        return new_status

    def update(self, db: Session, **kwargs):
        """Update status fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.fechaUltimaModificacion = datetime.utcnow()
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        """Delete status"""
        db.delete(self)
        db.commit()

    def __repr__(self):
        return f'<StatusDevice {self.id}: {self.descripcion}>'