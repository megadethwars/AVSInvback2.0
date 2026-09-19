"""Usuarios ORM model and schema helpers for FastAPI controllers."""

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Integer, MetaData, String, Table, Text, cast, select
from sqlalchemy.orm import Session

from . import Base
from ..database import engine
from ..schemas import ORMBaseModel, UsuarioLogin, UsuariosBase, UsuariosCreate, UsuariosQuery, UsuariosUpdate


class UsuariosModel(Base):
    __tablename__ = "invUsuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(45))
    username = Column(String(45), nullable=False)
    apellidoPaterno = Column(String(45))
    apellidoMaterno = Column(String(45))
    password = Column(Text, nullable=False)
    telefono = Column(String(100))
    correo = Column(String(100))
    foto = Column(Text)
    rolId = Column(Integer, nullable=False)
    statusId = Column(Integer, nullable=False)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, data: dict | None = None, **kwargs):
        payload = data or kwargs
        self.nombre = payload.get("nombre")
        self.username = payload.get("username")
        self.apellidoPaterno = payload.get("apellidoPaterno")
        self.apellidoMaterno = payload.get("apellidoMaterno")
        self.password = payload.get("password")
        self.telefono = payload.get("telefono")
        self.correo = payload.get("correo")
        self.foto = payload.get("foto")
        self.rolId = payload.get("rolId")
        self.statusId = payload.get("statusId")
        self.fechaAlta = payload.get("fechaAlta") or datetime.utcnow()
        self.fechaUltimaModificacion = payload.get("fechaUltimaModificacion") or datetime.utcnow()

    @staticmethod
    def _json_safe_value(value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: UsuariosModel._json_safe_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [UsuariosModel._json_safe_value(item) for item in value]
        return value

    @staticmethod
    def _base_join_stmt():
        usuarios_tbl = UsuariosModel.__table__
        return (
            select(
                usuarios_tbl.c.id.label("usuario_id"),
                usuarios_tbl.c.nombre.label("usuario_nombre"),
                usuarios_tbl.c.username.label("usuario_username"),
                usuarios_tbl.c.apellidoPaterno.label("usuario_apellidoPaterno"),
                usuarios_tbl.c.apellidoMaterno.label("usuario_apellidoMaterno"),
                usuarios_tbl.c.password.label("usuario_password"),
                usuarios_tbl.c.telefono.label("usuario_telefono"),
                usuarios_tbl.c.correo.label("usuario_correo"),
                usuarios_tbl.c.foto.label("usuario_foto"),
                usuarios_tbl.c.rolId.label("usuario_rolId"),
                usuarios_tbl.c.statusId.label("usuario_statusId"),
                usuarios_tbl.c.fechaAlta.label("usuario_fechaAlta"),
                usuarios_tbl.c.fechaUltimaModificacion.label("usuario_fechaUltimaModificacion"),
                _roles.c.id.label("rol_id"),
                _roles.c.nombre.label("rol_nombre"),
                _roles.c.fechaAlta.label("rol_fechaAlta"),
                _roles.c.fechaUltimaModificacion.label("rol_fechaUltimaModificacion"),
                _status_usuarios.c.id.label("status_id"),
                _status_usuarios.c.descripcion.label("status_descripcion"),
                _status_usuarios.c.fechaAlta.label("status_fechaAlta"),
                _status_usuarios.c.fechaUltimaModificacion.label("status_fechaUltimaModificacion"),
            )
            .select_from(
                usuarios_tbl.outerjoin(_roles, _roles.c.id == usuarios_tbl.c.rolId).outerjoin(_status_usuarios, _status_usuarios.c.id == usuarios_tbl.c.statusId)
            )
        )

    @staticmethod
    def _build_from_row(row: dict) -> dict:
        usuario = {
            "id": row.get("usuario_id"),
            "nombre": row.get("usuario_nombre"),
            "username": row.get("usuario_username"),
            "apellidoPaterno": row.get("usuario_apellidoPaterno"),
            "apellidoMaterno": row.get("usuario_apellidoMaterno"),
            "password": row.get("usuario_password"),
            "telefono": row.get("usuario_telefono"),
            "correo": row.get("usuario_correo"),
            "foto": row.get("usuario_foto"),
            "rolId": row.get("usuario_rolId"),
            "statusId": row.get("usuario_statusId"),
            "fechaAlta": row.get("usuario_fechaAlta"),
            "fechaUltimaModificacion": row.get("usuario_fechaUltimaModificacion"),
        }

        rol = {
            "id": row.get("rol_id"),
            "nombre": row.get("rol_nombre"),
            "fechaAlta": row.get("rol_fechaAlta"),
            "fechaUltimaModificacion": row.get("rol_fechaUltimaModificacion"),
        }
        status_usuario = {
            "id": row.get("status_id"),
            "descripcion": row.get("status_descripcion"),
            "fechaAlta": row.get("status_fechaAlta"),
            "fechaUltimaModificacion": row.get("status_fechaUltimaModificacion"),
        }

        usuario["rol"] = rol if any(v is not None for v in rol.values()) else None
        usuario["status"] = status_usuario if any(v is not None for v in status_usuario.values()) else None
        return UsuariosModel._json_safe_value(usuario)

    @staticmethod
    def fetch_by_id(db: Session, usuario_id: int) -> dict | None:
        stmt = UsuariosModel._base_join_stmt().where(UsuariosModel.__table__.c.id == usuario_id).limit(1)
        row = db.execute(stmt).mappings().first()
        if not row:
            return None
        return UsuariosModel._build_from_row(dict(row))

    @staticmethod
    def list_active(db: Session) -> list[dict]:
        stmt = UsuariosModel._base_join_stmt().where(UsuariosModel.__table__.c.statusId != 3).order_by(UsuariosModel.__table__.c.id)
        rows = db.execute(stmt).mappings().all()
        return [UsuariosModel._build_from_row(dict(row)) for row in rows]

    @staticmethod
    def get_credentials_row(db: Session, username: str):
        stmt = (
            select(UsuariosModel.__table__.c.id, UsuariosModel.__table__.c.password, UsuariosModel.__table__.c.statusId)
            .where(UsuariosModel.__table__.c.username == username)
            .limit(1)
        )
        return db.execute(stmt).mappings().first()

    @staticmethod
    def exists_username(db: Session, username: str) -> bool:
        stmt = select(UsuariosModel.__table__.c.id).where(UsuariosModel.__table__.c.username == username).limit(1)
        return db.execute(stmt).scalar_one_or_none() is not None

    @staticmethod
    def create_user(db: Session, data: dict):
        row = UsuariosModel(data)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row


_metadata = MetaData()
_roles = Table("invRoles", _metadata, autoload_with=engine)
_status_usuarios = Table("invStatusUsuarios", _metadata, autoload_with=engine)

UsuariosSchema = UsuariosBase
UsuariosSchemaCreate = UsuariosCreate
UsuariosSchemaUpdate = UsuariosUpdate
UsuariosSchemaQuery = UsuariosQuery
UsuariosLoginSchema = UsuarioLogin


__all__ = [
    "UsuariosModel",
    "UsuariosBase",
    "UsuariosCreate",
    "UsuariosUpdate",
    "UsuariosQuery",
    "UsuarioLogin",
    "UsuariosSchema",
    "UsuariosSchemaCreate",
    "UsuariosSchemaUpdate",
    "UsuariosSchemaQuery",
    "UsuariosLoginSchema",
    "ORMBaseModel",
]