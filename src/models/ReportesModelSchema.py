"""Reportes ORM model and nested response query helpers for FastAPI controllers."""

from datetime import date, datetime

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, select
from sqlalchemy.orm import Session

from . import Base
from .DispositivosModel import DispositivosModel
from ..database import engine
from ..schemas import ORMBaseModel, ReportesBase, ReportesCreate, ReportesQuery, ReportesUpdate


class ReportesModel(Base):
    __tablename__ = "invReportes"

    id = Column(Integer, primary_key=True, index=True)
    dispositivoId = Column(Integer, nullable=False)
    usuarioId = Column(Integer, nullable=False)
    comentarios = Column(Text)
    foto = Column(Text)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, data: dict | None = None, **kwargs):
        payload = data or kwargs
        self.dispositivoId = payload.get("dispositivoId")
        self.usuarioId = payload.get("usuarioId")
        self.comentarios = payload.get("comentarios")
        self.foto = payload.get("foto")
        self.fechaAlta = payload.get("fechaAlta") or datetime.utcnow()
        self.fechaUltimaModificacion = payload.get("fechaUltimaModificacion") or datetime.utcnow()

    @staticmethod
    def _json_safe_value(value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: ReportesModel._json_safe_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [ReportesModel._json_safe_value(item) for item in value]
        return value

    @staticmethod
    def _base_join_stmt():
        reportes_tbl = ReportesModel.__table__
        dispositivos_tbl = DispositivosModel.__table__
        device_lugar = _lugares.alias("device_lugar")

        return (
            select(
                reportes_tbl.c.id.label("reporte_id"),
                reportes_tbl.c.dispositivoId.label("reporte_dispositivoId"),
                reportes_tbl.c.usuarioId.label("reporte_usuarioId"),
                reportes_tbl.c.comentarios.label("reporte_comentarios"),
                reportes_tbl.c.foto.label("reporte_foto"),
                reportes_tbl.c.fechaAlta.label("reporte_fechaAlta"),
                reportes_tbl.c.fechaUltimaModificacion.label("reporte_fechaUltimaModificacion"),
                dispositivos_tbl.c.id.label("dispositivo_id"),
                dispositivos_tbl.c.codigo.label("dispositivo_codigo"),
                dispositivos_tbl.c.producto.label("dispositivo_producto"),
                dispositivos_tbl.c.marca.label("dispositivo_marca"),
                dispositivos_tbl.c.modelo.label("dispositivo_modelo"),
                dispositivos_tbl.c.origen.label("dispositivo_origen"),
                dispositivos_tbl.c.foto.label("dispositivo_foto"),
                dispositivos_tbl.c.cantidad.label("dispositivo_cantidad"),
                dispositivos_tbl.c.observaciones.label("dispositivo_observaciones"),
                dispositivos_tbl.c.lugarId.label("dispositivo_lugarId"),
                dispositivos_tbl.c.pertenece.label("dispositivo_pertenece"),
                dispositivos_tbl.c.descompostura.label("dispositivo_descompostura"),
                dispositivos_tbl.c.costo.label("dispositivo_costo"),
                dispositivos_tbl.c.compra.label("dispositivo_compra"),
                dispositivos_tbl.c.proveedor.label("dispositivo_proveedor"),
                dispositivos_tbl.c.idMov.label("dispositivo_idMov"),
                dispositivos_tbl.c.statusId.label("dispositivo_statusId"),
                dispositivos_tbl.c.fechaAlta.label("dispositivo_fechaAlta"),
                dispositivos_tbl.c.fechaUltimaModificacion.label("dispositivo_fechaUltimaModificacion"),
                dispositivos_tbl.c.serie.label("dispositivo_serie"),
                dispositivos_tbl.c.accesorios.label("dispositivo_accesorios"),
                device_lugar.c.id.label("dispositivo_lugar_id"),
                device_lugar.c.lugar.label("dispositivo_lugar_lugar"),
                device_lugar.c.activo.label("dispositivo_lugar_activo"),
                device_lugar.c.fechaAlta.label("dispositivo_lugar_fechaAlta"),
                device_lugar.c.fechaUltimaModificacion.label("dispositivo_lugar_fechaUltimaModificacion"),
                _status_devices.c.id.label("dispositivo_status_id"),
                _status_devices.c.descripcion.label("dispositivo_status_descripcion"),
                _status_devices.c.fechaAlta.label("dispositivo_status_fechaAlta"),
                _status_devices.c.fechaUltimaModificacion.label("dispositivo_status_fechaUltimaModificacion"),
                _usuarios.c.id.label("usuario_id"),
                _usuarios.c.nombre.label("usuario_nombre"),
                _usuarios.c.username.label("usuario_username"),
                _usuarios.c.apellidoPaterno.label("usuario_apellidoPaterno"),
                _usuarios.c.apellidoMaterno.label("usuario_apellidoMaterno"),
                _usuarios.c.telefono.label("usuario_telefono"),
                _usuarios.c.correo.label("usuario_correo"),
                _usuarios.c.foto.label("usuario_foto"),
                _usuarios.c.rolId.label("usuario_rolId"),
                _usuarios.c.statusId.label("usuario_statusId"),
                _usuarios.c.fechaAlta.label("usuario_fechaAlta"),
                _usuarios.c.fechaUltimaModificacion.label("usuario_fechaUltimaModificacion"),
                _roles.c.id.label("usuario_rol_id"),
                _roles.c.nombre.label("usuario_rol_nombre"),
                _roles.c.fechaAlta.label("usuario_rol_fechaAlta"),
                _roles.c.fechaUltimaModificacion.label("usuario_rol_fechaUltimaModificacion"),
                _status_usuarios.c.id.label("usuario_status_obj_id"),
                _status_usuarios.c.descripcion.label("usuario_status_obj_descripcion"),
                _status_usuarios.c.fechaAlta.label("usuario_status_obj_fechaAlta"),
                _status_usuarios.c.fechaUltimaModificacion.label("usuario_status_obj_fechaUltimaModificacion"),
            )
            .select_from(
                reportes_tbl.join(dispositivos_tbl, dispositivos_tbl.c.id == reportes_tbl.c.dispositivoId)
                .outerjoin(device_lugar, device_lugar.c.id == dispositivos_tbl.c.lugarId)
                .outerjoin(_status_devices, _status_devices.c.id == dispositivos_tbl.c.statusId)
                .outerjoin(_usuarios, _usuarios.c.id == reportes_tbl.c.usuarioId)
                .outerjoin(_roles, _roles.c.id == _usuarios.c.rolId)
                .outerjoin(_status_usuarios, _status_usuarios.c.id == _usuarios.c.statusId)
            )
        )

    @staticmethod
    def _build_from_row(row: dict) -> dict:
        reporte = {
            "id": row.get("reporte_id"),
            "dispositivoId": row.get("reporte_dispositivoId"),
            "usuarioId": row.get("reporte_usuarioId"),
            "comentarios": row.get("reporte_comentarios"),
            "foto": row.get("reporte_foto"),
            "fechaAlta": row.get("reporte_fechaAlta"),
            "fechaUltimaModificacion": row.get("reporte_fechaUltimaModificacion"),
        }

        dispositivo = {
            "id": row.get("dispositivo_id"),
            "codigo": row.get("dispositivo_codigo"),
            "producto": row.get("dispositivo_producto"),
            "marca": row.get("dispositivo_marca"),
            "modelo": row.get("dispositivo_modelo"),
            "origen": row.get("dispositivo_origen"),
            "foto": row.get("dispositivo_foto"),
            "cantidad": row.get("dispositivo_cantidad"),
            "observaciones": row.get("dispositivo_observaciones"),
            "lugarId": row.get("dispositivo_lugarId"),
            "pertenece": row.get("dispositivo_pertenece"),
            "descompostura": row.get("dispositivo_descompostura"),
            "costo": row.get("dispositivo_costo"),
            "compra": row.get("dispositivo_compra"),
            "proveedor": row.get("dispositivo_proveedor"),
            "idMov": row.get("dispositivo_idMov"),
            "statusId": row.get("dispositivo_statusId"),
            "fechaAlta": row.get("dispositivo_fechaAlta"),
            "fechaUltimaModificacion": row.get("dispositivo_fechaUltimaModificacion"),
            "serie": row.get("dispositivo_serie"),
            "accesorios": row.get("dispositivo_accesorios"),
        }
        dispositivo_lugar = {
            "id": row.get("dispositivo_lugar_id"),
            "lugar": row.get("dispositivo_lugar_lugar"),
            "activo": row.get("dispositivo_lugar_activo"),
            "fechaAlta": row.get("dispositivo_lugar_fechaAlta"),
            "fechaUltimaModificacion": row.get("dispositivo_lugar_fechaUltimaModificacion"),
        }
        dispositivo_status = {
            "id": row.get("dispositivo_status_id"),
            "descripcion": row.get("dispositivo_status_descripcion"),
            "fechaAlta": row.get("dispositivo_status_fechaAlta"),
            "fechaUltimaModificacion": row.get("dispositivo_status_fechaUltimaModificacion"),
        }
        dispositivo["lugar"] = dispositivo_lugar if any(v is not None for v in dispositivo_lugar.values()) else None
        dispositivo["status"] = dispositivo_status if any(v is not None for v in dispositivo_status.values()) else None

        usuario = {
            "id": row.get("usuario_id"),
            "nombre": row.get("usuario_nombre"),
            "username": row.get("usuario_username"),
            "apellidoPaterno": row.get("usuario_apellidoPaterno"),
            "apellidoMaterno": row.get("usuario_apellidoMaterno"),
            "telefono": row.get("usuario_telefono"),
            "correo": row.get("usuario_correo"),
            "foto": row.get("usuario_foto"),
            "rolId": row.get("usuario_rolId"),
            "statusId": row.get("usuario_statusId"),
            "fechaAlta": row.get("usuario_fechaAlta"),
            "fechaUltimaModificacion": row.get("usuario_fechaUltimaModificacion"),
        }
        usuario_rol = {
            "id": row.get("usuario_rol_id"),
            "nombre": row.get("usuario_rol_nombre"),
            "fechaAlta": row.get("usuario_rol_fechaAlta"),
            "fechaUltimaModificacion": row.get("usuario_rol_fechaUltimaModificacion"),
        }
        usuario_status = {
            "id": row.get("usuario_status_obj_id"),
            "descripcion": row.get("usuario_status_obj_descripcion"),
            "fechaAlta": row.get("usuario_status_obj_fechaAlta"),
            "fechaUltimaModificacion": row.get("usuario_status_obj_fechaUltimaModificacion"),
        }
        usuario["rol"] = usuario_rol if any(v is not None for v in usuario_rol.values()) else None
        usuario["status"] = usuario_status if any(v is not None for v in usuario_status.values()) else None

        reporte["dispositivo"] = dispositivo if any(v is not None for v in dispositivo.values()) else None
        reporte["usuario"] = usuario if any(v is not None for v in usuario.values()) else None
        return ReportesModel._json_safe_value(reporte)

    @staticmethod
    def fetch_by_id(db: Session, reporte_id: int) -> dict | None:
        stmt = ReportesModel._base_join_stmt().where(ReportesModel.__table__.c.id == reporte_id).limit(1)
        row = db.execute(stmt).mappings().first()
        if not row:
            return None
        return ReportesModel._build_from_row(dict(row))

    @staticmethod
    def list_all(db: Session) -> list[dict]:
        rows = db.execute(ReportesModel._base_join_stmt().order_by(ReportesModel.__table__.c.id.desc())).mappings().all()
        return [ReportesModel._build_from_row(dict(row)) for row in rows]

    @staticmethod
    def create_reporte(db: Session, data: dict):
        row = ReportesModel(data)
        db.add(row)
        db.flush()
        return row


_metadata = MetaData()
_lugares = Table("invLugares", _metadata, autoload_with=engine)
_status_devices = Table("invStatusDevices", _metadata, autoload_with=engine)
_usuarios = Table("invUsuarios", _metadata, autoload_with=engine)
_roles = Table("invRoles", _metadata, autoload_with=engine)
_status_usuarios = Table("invStatusUsuarios", _metadata, autoload_with=engine)

ReportesSchema = ReportesBase
ReportesSchemaCreate = ReportesCreate
ReportesSchemaUpdate = ReportesUpdate
ReportesSchemaQuery = ReportesQuery


__all__ = [
    "ReportesModel",
    "ReportesBase",
    "ReportesCreate",
    "ReportesUpdate",
    "ReportesQuery",
    "ReportesSchema",
    "ReportesSchemaCreate",
    "ReportesSchemaUpdate",
    "ReportesSchemaQuery",
    "ORMBaseModel",
]