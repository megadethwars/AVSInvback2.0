"""EstatusUsuarios ORM model and schema exports for FastAPI controllers."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.orm import Session

from . import Base
from ..schemas import EstatusUsuariosBase, EstatusUsuariosCreate, EstatusUsuariosUpdate, ORMBaseModel


class EstatusUsuariosModel(Base):
    __tablename__ = "invStatusUsuarios"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(100), nullable=False)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, data: dict | None = None, **kwargs):
        payload = data or kwargs
        self.descripcion = payload.get("descripcion")
        self.fechaAlta = payload.get("fechaAlta") or datetime.utcnow()
        self.fechaUltimaModificacion = payload.get("fechaUltimaModificacion") or datetime.utcnow()

    def update(self, db: Session, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.fechaUltimaModificacion = datetime.utcnow()
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    @staticmethod
    def to_dict(row: "EstatusUsuariosModel") -> dict:
        return {
            "id": row.id,
            "descripcion": row.descripcion,
            "fechaAlta": row.fechaAlta.isoformat() if row.fechaAlta else None,
            "fechaUltimaModificacion": row.fechaUltimaModificacion.isoformat() if row.fechaUltimaModificacion else None,
        }

    @staticmethod
    def get_all_status(db: Session):
        stmt = select(EstatusUsuariosModel).order_by(EstatusUsuariosModel.id)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_one_status(db: Session, status_id: int):
        stmt = select(EstatusUsuariosModel).where(EstatusUsuariosModel.id == status_id).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_status_by_tipo(db: Session, descripcion: str):
        stmt = select(EstatusUsuariosModel).where(EstatusUsuariosModel.descripcion == descripcion).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create_status(db: Session, descripcion: str):
        row = EstatusUsuariosModel({"descripcion": descripcion})
        db.add(row)
        db.commit()
        db.refresh(row)
        return row


EstatusUsuariosSchema = EstatusUsuariosBase
EstatusUsuariosSchemaCreate = EstatusUsuariosCreate
EstatusUsuariosSchemaUpdate = EstatusUsuariosUpdate


__all__ = [
    "EstatusUsuariosModel",
    "EstatusUsuariosBase",
    "EstatusUsuariosCreate",
    "EstatusUsuariosUpdate",
    "EstatusUsuariosSchema",
    "EstatusUsuariosSchemaCreate",
    "EstatusUsuariosSchemaUpdate",
    "ORMBaseModel",
]