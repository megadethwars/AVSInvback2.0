"""StatusLugar model/schema aggregation built over invLugares."""

from .LugaresModel import LugaresModel
from ..schemas import LugaresBase, LugaresCreate, LugaresUpdate, ORMBaseModel


class StatusLugarModelSchema:
    @staticmethod
    def to_dict(row: LugaresModel) -> dict:
        return {
            "id": row.id,
            "descripcion": row.lugar,
            "activo": row.activo,
            "fechaAlta": row.fechaAlta.isoformat() if row.fechaAlta else None,
            "fechaUltimaModificacion": row.fechaUltimaModificacion.isoformat() if row.fechaUltimaModificacion else None,
        }


StatusLugarSchema = LugaresBase
StatusLugarSchemaCreate = LugaresCreate
StatusLugarSchemaUpdate = LugaresUpdate


__all__ = [
    "LugaresModel",
    "StatusLugarModelSchema",
    "StatusLugarSchema",
    "StatusLugarSchemaCreate",
    "StatusLugarSchemaUpdate",
    "ORMBaseModel",
]