"""Roles ORM model and schema exports for FastAPI controllers."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.orm import Session

from . import Base
from ..schemas import RolesBase, RolesCreate, RolesUpdate, ORMBaseModel


class RolesModel(Base):
    __tablename__ = "invRoles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(45), nullable=False)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, data: dict | None = None, **kwargs):
        payload = data or kwargs
        self.nombre = payload.get("nombre")
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
    def to_dict(row: "RolesModel") -> dict:
        return {
            "id": row.id,
            "nombre": row.nombre,
            "fechaAlta": row.fechaAlta.isoformat() if row.fechaAlta else None,
            "fechaUltimaModificacion": row.fechaUltimaModificacion.isoformat() if row.fechaUltimaModificacion else None,
        }

    @staticmethod
    def get_all_roles(db: Session):
        stmt = select(RolesModel).order_by(RolesModel.nombre)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_one_rol(db: Session, role_id: int):
        stmt = select(RolesModel).where(RolesModel.id == role_id).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_rol_by_nombre(db: Session, nombre: str):
        stmt = select(RolesModel).where(RolesModel.nombre == nombre).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create_role(db: Session, nombre: str):
        row = RolesModel({"nombre": nombre})
        db.add(row)
        db.commit()
        db.refresh(row)
        return row


RolesSchema = RolesBase
RolesSchemaCreate = RolesCreate
RolesSchemaUpdate = RolesUpdate


__all__ = [
    "RolesModel",
    "RolesBase",
    "RolesCreate",
    "RolesUpdate",
    "RolesSchema",
    "RolesSchemaCreate",
    "RolesSchemaUpdate",
    "ORMBaseModel",
]