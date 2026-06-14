"""Movimientos ORM model for the FastAPI code path.

This module keeps persistence concerns in the models layer and re-exports the
Pydantic schemas used by FastAPI controllers.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, MetaData, String, Table, Text, cast, func, select
from sqlalchemy.orm import Session, relationship

from . import Base
from .DispositivosModel import DispositivosModel
from .LugaresModel import LugaresModel
from ..database import engine
from ..schemas import (
    MovimientosBase,
    MovimientosCreate,
    MovimientosQuery,
    MovimientosSomeFields,
    MovimientosUpdate,
    ORMBaseModel,
)


class MovimientosModel(Base):
    """SQLAlchemy ORM model for table invMovimientos."""

    __tablename__ = "invMovimientos"

    id = Column(Integer, primary_key=True, index=True)
    idMovimiento = Column(String(200))
    dispositivoId = Column(Integer, ForeignKey("invDispositivos.id"), nullable=False)
    usuarioId = Column(Integer, nullable=False)
    tipoMovId = Column(Integer, nullable=False)
    LugarId = Column(Integer, ForeignKey("invLugares.id"), nullable=False)
    comentarios = Column(Text)
    foto = Column(Text)
    foto2 = Column(Text)
    fechaAlta = Column(DateTime, default=datetime.utcnow)
    fechaUltimaModificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cantidad_Actual = Column(Integer, default=0)

    dispositivo = relationship("DispositivosModel", backref="movimientos")
    lugar = relationship("LugaresModel", foreign_keys=[LugarId], backref="movimientos")

    def __init__(self, data: Optional[dict] = None, **kwargs):
        payload = data or kwargs

        self.idMovimiento = payload.get("idMovimiento")
        self.dispositivoId = payload.get("dispositivoId")
        self.usuarioId = payload.get("usuarioId")
        self.tipoMovId = payload.get("tipoMovId")
        self.LugarId = payload.get("LugarId")
        self.comentarios = payload.get("comentarios")
        self.foto = payload.get("foto")
        self.foto2 = payload.get("foto2")
        self.cantidad_Actual = payload.get("cantidad_Actual")
        self.fechaAlta = payload.get("fechaAlta") or datetime.utcnow()
        self.fechaUltimaModificacion = payload.get("fechaUltimaModificacion") or datetime.utcnow()

    def save(self, db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def update(self, db: Session, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.fechaUltimaModificacion = datetime.utcnow()
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        db.delete(self)
        db.commit()

    @staticmethod
    def get_one_movimiento(db: Session, movimiento_id: int):
        stmt = select(MovimientosModel).where(MovimientosModel.id == movimiento_id).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_lastone_movimiento(db: Session, dispositivo_id: int):
        stmt = (
            select(MovimientosModel)
            .where(MovimientosModel.dispositivoId == dispositivo_id, MovimientosModel.tipoMovId == 1)
            .order_by(MovimientosModel.fechaAlta.desc())
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def _json_safe_value(value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: MovimientosModel._json_safe_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [MovimientosModel._json_safe_value(item) for item in value]
        return value

    @staticmethod
    def usuario_exists(db: Session, usuario_id: int) -> bool:
        stmt = select(_usuarios.c.id).where(_usuarios.c.id == usuario_id).limit(1)
        return db.execute(stmt).scalar_one_or_none() is not None

    @staticmethod
    def tipo_mov_exists(db: Session, tipo_mov_id: int) -> bool:
        stmt = select(_tipomoves.c.id).where(_tipomoves.c.id == tipo_mov_id).limit(1)
        return db.execute(stmt).scalar_one_or_none() is not None

    @staticmethod
    def _base_join_stmt():
        movimientos_tbl = MovimientosModel.__table__
        device_tbl = DispositivosModel.__table__
        lugar_tbl = LugaresModel.__table__

        device_lugar = lugar_tbl.alias("device_lugar")
        mov_lugar = lugar_tbl.alias("mov_lugar")

        return (
            select(
                movimientos_tbl.c.id.label("movimiento_id"),
                movimientos_tbl.c.idMovimiento.label("movimiento_idMovimiento"),
                movimientos_tbl.c.dispositivoId.label("movimiento_dispositivoId"),
                movimientos_tbl.c.usuarioId.label("movimiento_usuarioId"),
                movimientos_tbl.c.tipoMovId.label("movimiento_tipoMovId"),
                movimientos_tbl.c.LugarId.label("movimiento_LugarId"),
                movimientos_tbl.c.comentarios.label("movimiento_comentarios"),
                movimientos_tbl.c.foto.label("movimiento_foto"),
                movimientos_tbl.c.foto2.label("movimiento_foto2"),
                movimientos_tbl.c.fechaAlta.label("movimiento_fechaAlta"),
                movimientos_tbl.c.fechaUltimaModificacion.label("movimiento_fechaUltimaModificacion"),
                movimientos_tbl.c.cantidad_Actual.label("movimiento_cantidad_Actual"),
                device_tbl.c.id.label("dispositivo_id"),
                device_tbl.c.codigo.label("dispositivo_codigo"),
                device_tbl.c.producto.label("dispositivo_producto"),
                device_tbl.c.marca.label("dispositivo_marca"),
                device_tbl.c.modelo.label("dispositivo_modelo"),
                device_tbl.c.origen.label("dispositivo_origen"),
                device_tbl.c.foto.label("dispositivo_foto"),
                device_tbl.c.cantidad.label("dispositivo_cantidad"),
                device_tbl.c.observaciones.label("dispositivo_observaciones"),
                device_tbl.c.lugarId.label("dispositivo_lugarId"),
                device_tbl.c.pertenece.label("dispositivo_pertenece"),
                device_tbl.c.descompostura.label("dispositivo_descompostura"),
                device_tbl.c.costo.label("dispositivo_costo"),
                device_tbl.c.compra.label("dispositivo_compra"),
                device_tbl.c.proveedor.label("dispositivo_proveedor"),
                device_tbl.c.idMov.label("dispositivo_idMov"),
                device_tbl.c.statusId.label("dispositivo_statusId"),
                device_tbl.c.serie.label("dispositivo_serie"),
                device_tbl.c.accesorios.label("dispositivo_accesorios"),
                device_lugar.c.id.label("dispositivo_lugar_id"),
                device_lugar.c.lugar.label("dispositivo_lugar_lugar"),
                device_lugar.c.activo.label("dispositivo_lugar_activo"),
                device_lugar.c.fechaAlta.label("dispositivo_lugar_fechaAlta"),
                device_lugar.c.fechaUltimaModificacion.label("dispositivo_lugar_fechaUltimaModificacion"),
                _status_devices.c.id.label("dispositivo_status_id"),
                _status_devices.c.descripcion.label("dispositivo_status_descripcion"),
                _status_devices.c.fechaAlta.label("dispositivo_status_fechaAlta"),
                _status_devices.c.fechaUltimaModificacion.label("dispositivo_status_fechaUltimaModificacion"),
                mov_lugar.c.id.label("lugar_id"),
                mov_lugar.c.lugar.label("lugar_lugar"),
                mov_lugar.c.activo.label("lugar_activo"),
                mov_lugar.c.fechaAlta.label("lugar_fechaAlta"),
                mov_lugar.c.fechaUltimaModificacion.label("lugar_fechaUltimaModificacion"),
                _tipomoves.c.id.label("tipoMovimiento_id"),
                _tipomoves.c.tipo.label("tipoMovimiento_tipo"),
                _tipomoves.c.fechaAlta.label("tipoMovimiento_fechaAlta"),
                _tipomoves.c.fechaUltimaModificacion.label("tipoMovimiento_fechaUltimaModificacion"),
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
                movimientos_tbl.join(device_tbl, device_tbl.c.id == movimientos_tbl.c.dispositivoId)
                .outerjoin(device_lugar, device_lugar.c.id == device_tbl.c.lugarId)
                .outerjoin(_status_devices, _status_devices.c.id == device_tbl.c.statusId)
                .outerjoin(mov_lugar, mov_lugar.c.id == movimientos_tbl.c.LugarId)
                .outerjoin(_tipomoves, _tipomoves.c.id == movimientos_tbl.c.tipoMovId)
                .outerjoin(_usuarios, _usuarios.c.id == movimientos_tbl.c.usuarioId)
                .outerjoin(_roles, _roles.c.id == _usuarios.c.rolId)
                .outerjoin(_status_usuarios, _status_usuarios.c.id == _usuarios.c.statusId)
            )
        )

    @staticmethod
    def _build_from_joined_row(row: dict) -> dict:
        movimiento = {
            "id": row.get("movimiento_id"),
            "idMovimiento": row.get("movimiento_idMovimiento"),
            "dispositivoId": row.get("movimiento_dispositivoId"),
            "usuarioId": row.get("movimiento_usuarioId"),
            "tipoMovId": row.get("movimiento_tipoMovId"),
            "LugarId": row.get("movimiento_LugarId"),
            "comentarios": row.get("movimiento_comentarios"),
            "foto": row.get("movimiento_foto"),
            "foto2": row.get("movimiento_foto2"),
            "fechaAlta": row.get("movimiento_fechaAlta"),
            "fechaUltimaModificacion": row.get("movimiento_fechaUltimaModificacion"),
            "cantidad_Actual": row.get("movimiento_cantidad_Actual"),
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

        lugar = {
            "id": row.get("lugar_id"),
            "lugar": row.get("lugar_lugar"),
            "activo": row.get("lugar_activo"),
            "fechaAlta": row.get("lugar_fechaAlta"),
            "fechaUltimaModificacion": row.get("lugar_fechaUltimaModificacion"),
        }

        tipo_movimiento = {
            "id": row.get("tipoMovimiento_id"),
            "tipo": row.get("tipoMovimiento_tipo"),
            "fechaAlta": row.get("tipoMovimiento_fechaAlta"),
            "fechaUltimaModificacion": row.get("tipoMovimiento_fechaUltimaModificacion"),
        }

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

        movimiento["lugar"] = lugar if any(v is not None for v in lugar.values()) else None
        movimiento["dispositivo"] = dispositivo if any(v is not None for v in dispositivo.values()) else None
        movimiento["tipoMovimiento"] = tipo_movimiento if any(v is not None for v in tipo_movimiento.values()) else None
        movimiento["usuario"] = usuario if any(v is not None for v in usuario.values()) else None
        return MovimientosModel._json_safe_value(movimiento)

    @staticmethod
    def fetch_by_id(db: Session, movimiento_id: int) -> dict | None:
        stmt = MovimientosModel._base_join_stmt().where(MovimientosModel.__table__.c.id == movimiento_id).limit(1)
        row = db.execute(stmt).mappings().first()
        if not row:
            return None
        return MovimientosModel._build_from_joined_row(dict(row))

    @staticmethod
    def fetch_some_fields(
        db: Session,
        offset: int,
        limit: int,
        search_value: str | None = None,
    ) -> tuple[list[dict], int]:
        movimientos_tbl = MovimientosModel.__table__
        base_stmt = (
            select(
                movimientos_tbl.c.id,
                DispositivosModel.codigo,
                DispositivosModel.producto,
                movimientos_tbl.c.fechaAlta,
                movimientos_tbl.c.idMovimiento,
                LugaresModel.lugar,
                _tipomoves.c.tipo,
                _usuarios.c.nombre,
                _usuarios.c.username,
            )
            .select_from(
                movimientos_tbl.join(DispositivosModel, DispositivosModel.id == movimientos_tbl.c.dispositivoId)
                .outerjoin(LugaresModel, LugaresModel.id == movimientos_tbl.c.LugarId)
                .outerjoin(_tipomoves, _tipomoves.c.id == movimientos_tbl.c.tipoMovId)
                .outerjoin(_usuarios, _usuarios.c.id == movimientos_tbl.c.usuarioId)
            )
        )

        filters = []
        if search_value:
            pattern = f"%{search_value}%"
            filters.append(
                (
                    DispositivosModel.codigo.ilike(pattern)
                    | DispositivosModel.producto.ilike(pattern)
                    | movimientos_tbl.c.idMovimiento.ilike(pattern)
                    | LugaresModel.lugar.ilike(pattern)
                    | _tipomoves.c.tipo.ilike(pattern)
                    | _usuarios.c.nombre.ilike(pattern)
                    | _usuarios.c.username.ilike(pattern)
                )
            )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        if filters:
            count_stmt = select(func.count()).select_from(base_stmt.where(*filters).subquery())
        total_rows = int(db.execute(count_stmt).scalar() or 0)

        data_stmt = (
            base_stmt.where(*filters)
            .order_by(movimientos_tbl.c.fechaAlta.desc())
            .offset(int(offset))
            .limit(int(limit))
        )

        rows = db.execute(data_stmt).mappings().all()
        serialized = [MovimientosModel._json_safe_value(dict(row)) for row in rows]
        return serialized, total_rows

    @staticmethod
    def query_full(
        db: Session,
        payload: dict,
        offset: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        movimientos_tbl = MovimientosModel.__table__
        filters = []
        if "id" in payload and payload.get("id") is not None:
            filters.append(movimientos_tbl.c.id == payload.get("id"))
        if "dispositivoId" in payload and payload.get("dispositivoId") is not None:
            filters.append(movimientos_tbl.c.dispositivoId == payload.get("dispositivoId"))
        if "LugarId" in payload and payload.get("LugarId") is not None:
            filters.append(movimientos_tbl.c.LugarId == payload.get("LugarId"))
        if "tipoMovId" in payload and payload.get("tipoMovId") is not None:
            filters.append(movimientos_tbl.c.tipoMovId == payload.get("tipoMovId"))
        if "usuarioId" in payload and payload.get("usuarioId") is not None:
            filters.append(movimientos_tbl.c.usuarioId == payload.get("usuarioId"))
        if "idMovimiento" in payload and payload.get("idMovimiento"):
            filters.append(movimientos_tbl.c.idMovimiento.ilike(f"%{str(payload.get('idMovimiento')).strip()}%"))
        if "fechaAltaRangoInicio" in payload and payload.get("fechaAltaRangoInicio"):
            filters.append(cast(movimientos_tbl.c.fechaAlta, Date) >= payload.get("fechaAltaRangoInicio"))
        if "fechaAltaRangoFin" in payload and payload.get("fechaAltaRangoFin"):
            filters.append(cast(movimientos_tbl.c.fechaAlta, Date) <= payload.get("fechaAltaRangoFin"))

        if not filters:
            return [], 0

        count_stmt = select(func.count()).select_from(movimientos_tbl).where(*filters)
        total_rows = int(db.execute(count_stmt).scalar() or 0)

        id_stmt = (
            select(movimientos_tbl.c.id)
            .where(*filters)
            .order_by(movimientos_tbl.c.fechaAlta.desc())
            .offset(int(offset))
            .limit(int(limit))
        )
        ids = db.execute(id_stmt).scalars().all()

        if not ids:
            return [], total_rows

        index_by_id = {int(mov_id): idx for idx, mov_id in enumerate(ids)}
        rows_stmt = MovimientosModel._base_join_stmt().where(movimientos_tbl.c.id.in_(list(index_by_id.keys())))
        rows = db.execute(rows_stmt).mappings().all()

        movimientos_unsorted = [MovimientosModel._build_from_joined_row(dict(row)) for row in rows]
        movimientos = sorted(
            movimientos_unsorted,
            key=lambda item: index_by_id.get(int(item.get("id")), 0),
        )
        return movimientos, total_rows


_aux_metadata = MetaData()
_usuarios = Table("invUsuarios", _aux_metadata, autoload_with=engine)
_tipomoves = Table("invTipoMoves", _aux_metadata, autoload_with=engine)
_roles = Table("invRoles", _aux_metadata, autoload_with=engine)
_status_usuarios = Table("invStatusUsuarios", _aux_metadata, autoload_with=engine)
_status_devices = Table("invStatusDevices", _aux_metadata, autoload_with=engine)


# FastAPI-friendly schema exports.
MovimientosSchema = MovimientosBase
MovimientosSchemaCreate = MovimientosCreate
MovimientosSchemaUpdate = MovimientosUpdate
MovimientosSchemaQuery = MovimientosQuery
MovimientosSchemaSomeFields = MovimientosSomeFields


__all__ = [
    "MovimientosModel",
    "MovimientosBase",
    "MovimientosCreate",
    "MovimientosUpdate",
    "MovimientosQuery",
    "MovimientosSomeFields",
    "MovimientosSchema",
    "MovimientosSchemaCreate",
    "MovimientosSchemaUpdate",
    "MovimientosSchemaQuery",
    "MovimientosSchemaSomeFields",
    "ORMBaseModel",
]