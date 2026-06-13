"""Dispositivos Model using native SQLAlchemy 2.0"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, select, or_, and_
from sqlalchemy.orm import Session, relationship

from . import Base
from .LugaresModel import LugaresModel
from .StatusDevicesModel import StatusDevicesModel


class DispositivosModel(Base):
    """
    Dispositivos (Devices) Model
    Table: invDispositivos
    """
    
    __tablename__ = 'invDispositivos'

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), nullable=False)
    producto = Column(String(100), nullable=False)
    marca = Column(String(100))
    modelo = Column(String(100))
    origen = Column(String(100))
    foto = Column(Text)
    cantidad = Column(Integer, default=1)
    observaciones = Column(String(250))
    lugarId = Column(Integer, ForeignKey("invLugares.id"), nullable=False)
    statusId = Column(Integer, ForeignKey("invStatusDevices.id"), nullable=False)
    pertenece = Column(String(100))
    descompostura = Column(String(100))
    costo = Column(Integer)
    compra = Column(String(100))
    proveedor = Column(String(100))
    idMov = Column(Text)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    serie = Column(String(100))
    accesorios = Column(String(100))

    # Relationships
    lugar = relationship("LugaresModel", backref="dispositivos")
    status = relationship("StatusDevicesModel", backref="dispositivos")

    def __init__(self, codigo: str, producto: str, lugarId: int, statusId: int, **kwargs):
        """Initialize a new Dispositivo"""
        self.codigo = codigo
        self.producto = producto
        self.lugarId = lugarId
        self.statusId = statusId
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.fechaAlta = datetime.utcnow()
        self.fechaUltimaModificacion = datetime.utcnow()

    @staticmethod
    def get_all_devices(db: Session, offset: int = 0, limit: int = 10):
        """Get all devices with pagination"""
        query = select(DispositivosModel).order_by(DispositivosModel.producto).offset(offset).limit(limit)
        return db.execute(query).scalars().all()

    @staticmethod
    def get_one_device(db: Session, id: int):
        """Get a single device by ID"""
        query = select(DispositivosModel).where(DispositivosModel.id == id)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_devices_by_codigo(db: Session, value: str):
        """Get device by codigo"""
        query = select(DispositivosModel).where(DispositivosModel.codigo == value)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_devices_by_producto(db: Session, value: str):
        """Get device by producto"""
        query = select(DispositivosModel).where(DispositivosModel.producto == value)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def search_by_codigo(db: Session, value: str, offset: int = 0, limit: int = 10):
        """Search devices by codigo pattern"""
        query = (
            select(DispositivosModel)
            .where(DispositivosModel.codigo.ilike(f'%{value}%'))
            .order_by(DispositivosModel.producto)
            .offset(offset)
            .limit(limit)
        )
        return db.execute(query).scalars().all()

    @staticmethod
    def search_by_multiple_fields(db: Session, value: str, offset: int = 0, limit: int = 100):
        """Search devices by multiple fields"""
        search_pattern = f'%{value}%'
        query = (
            select(DispositivosModel)
            .where(
                or_(
                    DispositivosModel.codigo.ilike(search_pattern),
                    DispositivosModel.producto.ilike(search_pattern),
                    DispositivosModel.marca.ilike(search_pattern),
                    DispositivosModel.modelo.ilike(search_pattern),
                    DispositivosModel.serie.ilike(search_pattern),
                    DispositivosModel.accesorios.ilike(search_pattern),
                )
            )
            .order_by(DispositivosModel.producto)
            .offset(offset)
            .limit(limit)
        )
        return db.execute(query).scalars().all()

    @staticmethod
    def create_device(db: Session, **kwargs) -> 'DispositivosModel':
        """Create a new device"""
        # Guard against relationship/meta fields coming from Pydantic payloads.
        for key in ("id", "lugar", "status", "fechaAlta", "fechaUltimaModificacion"):
            kwargs.pop(key, None)
        new_device = DispositivosModel(**kwargs)
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return new_device

    def update(self, db: Session, **kwargs):
        """Update device fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.fechaUltimaModificacion = datetime.utcnow()
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        """Delete device"""
        db.delete(self)
        db.commit()

    def __repr__(self):
        return f'<Dispositivo {self.id}: {self.producto}>'
