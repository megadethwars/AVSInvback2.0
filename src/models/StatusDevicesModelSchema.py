"""StatusDevices model/schema aggregation for FastAPI controllers."""

from .StatusDevicesModel import StatusDevicesModel
from ..schemas import StatusDevicesBase, StatusDevicesCreate, StatusDevicesUpdate, ORMBaseModel


class StatusDevicesModelSchema:
    @staticmethod
    def to_dict(row: StatusDevicesModel) -> dict:
        return {
            "id": row.id,
            "descripcion": row.descripcion,
            "fechaAlta": row.fechaAlta.isoformat() if row.fechaAlta else None,
            "fechaUltimaModificacion": row.fechaUltimaModificacion.isoformat() if row.fechaUltimaModificacion else None,
        }


StatusDevicesSchema = StatusDevicesBase
StatusDevicesSchemaCreate = StatusDevicesCreate
StatusDevicesSchemaUpdate = StatusDevicesUpdate


__all__ = [
    "StatusDevicesModel",
    "StatusDevicesModelSchema",
    "StatusDevicesBase",
    "StatusDevicesCreate",
    "StatusDevicesUpdate",
    "StatusDevicesSchema",
    "StatusDevicesSchemaCreate",
    "StatusDevicesSchemaUpdate",
    "ORMBaseModel",
]