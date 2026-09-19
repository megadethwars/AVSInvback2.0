"""Lugares model/schema aggregation for FastAPI controllers."""

from .LugaresModel import LugaresModel
from ..schemas import LugaresBase, LugaresCreate, LugaresUpdate, ORMBaseModel


LugaresSchema = LugaresBase
LugaresSchemaCreate = LugaresCreate
LugaresSchemaUpdate = LugaresUpdate


__all__ = [
    "LugaresModel",
    "LugaresBase",
    "LugaresCreate",
    "LugaresUpdate",
    "LugaresSchema",
    "LugaresSchemaCreate",
    "LugaresSchemaUpdate",
    "ORMBaseModel",
]