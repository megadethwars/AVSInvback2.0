"""Job Movimientos ORM model and schema exports for FastAPI controllers."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, select
from sqlalchemy.orm import Session

from . import Base
from ..schemas import JobMovimientosBase, JobMovimientosCreate, JobMovimientosUpdate, ORMBaseModel


class JobMovimientosModel(Base):
    __tablename__ = "invJobMovimientos"

    id = Column(Integer, primary_key=True, index=True)
    idMovimiento = Column(Text)
    usuarioId = Column(Integer, ForeignKey("invUsuarios.id"), nullable=False)
    tipoMovId = Column(Integer, ForeignKey("invTipoMoves.id"), nullable=False)
    LugarId = Column(Integer, ForeignKey("invLugares.id"), nullable=False)
    comentarios = Column(Text)
    estado = Column(Text)
    status = Column(Integer, nullable=False)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, data: dict | None = None, **kwargs):
        payload = data or kwargs
        self.idMovimiento = payload.get("idMovimiento")
        self.usuarioId = payload.get("usuarioId")
        self.tipoMovId = payload.get("tipoMovId")
        self.LugarId = payload.get("LugarId")
        self.comentarios = payload.get("comentarios")
        self.estado = payload.get("estado")
        self.status = payload.get("status")
        self.fechaAlta = payload.get("fechaAlta") or datetime.utcnow()
        self.fechaUltimaModificacion = payload.get("fechaUltimaModificacion") or datetime.utcnow()

    @staticmethod
    def to_dict(row: "JobMovimientosModel") -> dict:
        return {
            "id": row.id,
            "idMovimiento": row.idMovimiento,
            "usuarioId": row.usuarioId,
            "tipoMovId": row.tipoMovId,
            "LugarId": row.LugarId,
            "comentarios": row.comentarios,
            "estado": row.estado,
            "status": row.status,
            "fechaAlta": row.fechaAlta.isoformat() if row.fechaAlta else None,
            "fechaUltimaModificacion": row.fechaUltimaModificacion.isoformat() if row.fechaUltimaModificacion else None,
        }

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
    def list_all(db: Session, offset: int = 0, limit: int = 100):
        stmt = (
            select(JobMovimientosModel)
            .order_by(JobMovimientosModel.fechaAlta.desc())
            .offset(int(offset))
            .limit(int(limit))
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_one(db: Session, job_id: int):
        stmt = select(JobMovimientosModel).where(JobMovimientosModel.id == job_id).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_latest_by_id_movimiento(db: Session, id_movimiento: str):
        stmt = (
            select(JobMovimientosModel)
            .where(JobMovimientosModel.idMovimiento == id_movimiento)
            .order_by(JobMovimientosModel.id.desc())
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create_job(db: Session, data: dict):
        row = JobMovimientosModel(data)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row


JobMovimientosSchema = JobMovimientosBase
JobMovimientosSchemaCreate = JobMovimientosCreate
JobMovimientosSchemaUpdate = JobMovimientosUpdate


__all__ = [
    "JobMovimientosModel",
    "JobMovimientosBase",
    "JobMovimientosCreate",
    "JobMovimientosUpdate",
    "JobMovimientosSchema",
    "JobMovimientosSchemaCreate",
    "JobMovimientosSchemaUpdate",
    "ORMBaseModel",
]
