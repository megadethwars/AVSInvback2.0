"""Dispositivos model/schema aggregation for FastAPI controllers."""

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from .DispositivosModel import DispositivosModel
from .LugaresModel import LugaresModel
from .StatusDevicesModel import StatusDevicesModel
from ..schemas import (
    DispositivosBase,
    DispositivosCantity,
    DispositivosCreate,
    DispositivosQuery,
    DispositivosSomeFields,
    DispositivosUpdate,
    ORMBaseModel,
)


class DispositivosModelSchema:
    """Helper facade to keep dispositivos controller thin."""

    @staticmethod
    def serialize_some_fields(device: DispositivosModel) -> dict:
        return {
            "id": device.id,
            "codigo": device.codigo,
            "producto": device.producto,
            "marca": device.marca,
            "modelo": device.modelo,
            "serie": device.serie,
            "lugar": device.lugar.lugar if device.lugar else None,
            "descripcion": device.status.descripcion if device.status else None,
        }

    @staticmethod
    def serialize_min_fields(device: DispositivosModel) -> dict:
        return {
            "id": device.id,
            "codigo": device.codigo,
            "producto": device.producto,
            "marca": device.marca,
            "modelo": device.modelo,
            "serie": device.serie,
            "cantidad": device.cantidad,
            "lugar": device.lugar.lugar if device.lugar else None,
            "descripcion": device.status.descripcion if device.status else None,
        }

    @staticmethod
    def query_devices(db: Session, filters_payload: dict, offset: int, limit: int):
        base_query = select(DispositivosModel)

        for field_name, field_value in filters_payload.items():
            if not hasattr(DispositivosModel, field_name):
                continue
            column = getattr(DispositivosModel, field_name)
            if isinstance(field_value, str):
                base_query = base_query.where(column.ilike(f"%{field_value}%"))
            else:
                base_query = base_query.where(column == field_value)

        return db.execute(
            base_query.order_by(DispositivosModel.producto).offset(offset).limit(limit)
        ).scalars().all()

    @staticmethod
    def filter_fields(
        db: Session,
        offset: int,
        limit: int,
        search_value: str = "",
        in_storage: int = 0,
        minimal: bool = False,
    ) -> tuple[list[dict], int]:
        base_query = (
            select(DispositivosModel)
            .join(LugaresModel, DispositivosModel.lugarId == LugaresModel.id, isouter=True)
            .join(StatusDevicesModel, DispositivosModel.statusId == StatusDevicesModel.id, isouter=True)
        )
        count_query = (
            select(func.count(func.distinct(DispositivosModel.id)))
            .select_from(DispositivosModel)
            .join(LugaresModel, DispositivosModel.lugarId == LugaresModel.id, isouter=True)
            .join(StatusDevicesModel, DispositivosModel.statusId == StatusDevicesModel.id, isouter=True)
        )

        if search_value:
            normalized_value = search_value.strip()
            terms = [term for term in normalized_value.split() if term]
            if not terms:
                terms = [normalized_value]

            term_filters = []
            for term in terms:
                pattern = f"%{term}%"
                searchable_fields = [
                    DispositivosModel.codigo.ilike(pattern),
                    DispositivosModel.producto.ilike(pattern),
                    DispositivosModel.marca.ilike(pattern),
                    DispositivosModel.modelo.ilike(pattern),
                    DispositivosModel.serie.ilike(pattern),
                    LugaresModel.lugar.ilike(pattern),
                    StatusDevicesModel.descripcion.ilike(pattern),
                ]

                if not minimal:
                    searchable_fields.append(DispositivosModel.accesorios.ilike(pattern))

                if term.isdigit():
                    searchable_fields.append(DispositivosModel.id == int(term))

                term_filters.append(or_(*searchable_fields))

            filters = and_(*term_filters)
            base_query = base_query.where(filters)
            count_query = count_query.where(filters)

        if int(in_storage) == 1:
            base_query = base_query.where(DispositivosModel.cantidad > 0)
            count_query = count_query.where(DispositivosModel.cantidad > 0)

        total_rows = int(db.execute(count_query).scalar() or 0)
        rows = db.execute(
            base_query.order_by(DispositivosModel.producto).offset(offset).limit(limit)
        ).scalars().all()

        if minimal:
            serialized = [DispositivosModelSchema.serialize_min_fields(row) for row in rows]
        else:
            serialized = [DispositivosModelSchema.serialize_some_fields(row) for row in rows]
        return serialized, total_rows

    @staticmethod
    def all_some_fields(db: Session, offset: int, limit: int) -> tuple[list[dict], int]:
        total_rows = int(db.execute(select(func.count()).select_from(DispositivosModel)).scalar() or 0)
        rows = db.execute(
            select(DispositivosModel).order_by(DispositivosModel.producto).offset(offset).limit(limit)
        ).scalars().all()
        serialized = [DispositivosModelSchema.serialize_some_fields(row) for row in rows]
        return serialized, total_rows

    @staticmethod
    def total_amount(db: Session) -> float:
        total_amount = db.execute(
            select(func.coalesce(func.sum(func.coalesce(DispositivosModel.costo, 0) * func.coalesce(DispositivosModel.cantidad, 0)), 0))
        ).scalar()
        return float(total_amount or 0)


DispositivosSchema = DispositivosBase
DispositivosSchemaCreate = DispositivosCreate
DispositivosSchemaUpdate = DispositivosUpdate
DispositivosSchemaQuery = DispositivosQuery
DispositivosSchemaSomeFields = DispositivosSomeFields
DispositivosSchemaCantity = DispositivosCantity


__all__ = [
    "DispositivosModel",
    "DispositivosModelSchema",
    "DispositivosBase",
    "DispositivosCreate",
    "DispositivosUpdate",
    "DispositivosQuery",
    "DispositivosSomeFields",
    "DispositivosCantity",
    "DispositivosSchema",
    "DispositivosSchemaCreate",
    "DispositivosSchemaUpdate",
    "DispositivosSchemaQuery",
    "DispositivosSchemaSomeFields",
    "DispositivosSchemaCantity",
    "ORMBaseModel",
]