"""TipoMovimientos ORM model and schema exports for FastAPI controllers."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.orm import Session

from . import Base
from ..schemas import ORMBaseModel, TipoMoveBase, TipoMoveCreate, TipoMoveUpdate


class TipoMovimientosModel(Base):
    __tablename__ = "invTipoMoves"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(45), nullable=False)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, data: dict | None = None, **kwargs):
        payload = data or kwargs
        self.tipo = payload.get("tipo")
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
    def to_dict(row: "TipoMovimientosModel") -> dict:
        return {
            "id": row.id,
            "tipo": row.tipo,
            "fechaAlta": row.fechaAlta.isoformat() if row.fechaAlta else None,
            "fechaUltimaModificacion": row.fechaUltimaModificacion.isoformat() if row.fechaUltimaModificacion else None,
        }

    @staticmethod
    def get_all_tipos(db: Session):
        stmt = select(TipoMovimientosModel).order_by(TipoMovimientosModel.id)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_one_tipo(db: Session, tipo_id: int):
        stmt = select(TipoMovimientosModel).where(TipoMovimientosModel.id == tipo_id).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_tipo_by_nombre(db: Session, tipo: str):
        stmt = select(TipoMovimientosModel).where(TipoMovimientosModel.tipo == tipo).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create_tipo(db: Session, tipo: str):
        row = TipoMovimientosModel({"tipo": tipo})
        db.add(row)
        db.commit()
        db.refresh(row)
        return row


TipoMovimientosSchema = TipoMoveBase
TipoMovimientosSchemaCreate = TipoMoveCreate
TipoMovimientosSchemaUpdate = TipoMoveUpdate


__all__ = [
    "TipoMovimientosModel",
    "TipoMoveBase",
    "TipoMoveCreate",
    "TipoMoveUpdate",
    "TipoMovimientosSchema",
    "TipoMovimientosSchemaCreate",
    "TipoMovimientosSchemaUpdate",
    "ORMBaseModel",
]