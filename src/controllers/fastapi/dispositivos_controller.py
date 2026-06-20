from fastapi import APIRouter, Body, Depends, Header, status
from sqlalchemy.orm import Session
import logging

from src.schemas import DispositivosBase
from ...database import get_db
from ...models.DispositivosModelSchema import (
    DispositivosModel,
    DispositivosModelSchema,
    DispositivosSchema,
    DispositivosSchemaCreate,
    DispositivosSchemaQuery,
    DispositivosSchemaUpdate,
)
from ...models.LugaresModel import LugaresModel
from ...models.StatusDevicesModel import StatusDevicesModel
from ...shared.returnCodes import fastapi_response, partial_response



router = APIRouter(prefix="/api/v1/dispositivos", tags=["Dispositivos"])
logger = logging.getLogger("uvicorn.error")
@router.get("", summary="Listar dispositivos")
async def get_dispositivos(
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    rows = DispositivosModel.get_all_devices(db, offset=offset, limit=limit)
    serialized = [DispositivosSchema.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/search/{search_term}", summary="Buscar dispositivos")
async def search_dispositivos(
    search_term: str,
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    rows = DispositivosModel.search_by_multiple_fields(db, search_term, offset, limit)
    if not rows:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = [DispositivosSchema.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear dispositivo")
async def create_dispositivo(
    dispositivo_data: DispositivosSchemaCreate,
    db: Session = Depends(get_db),
) -> dict:
    existing_device = DispositivosModel.get_devices_by_codigo(db, dispositivo_data.codigo)
    if existing_device:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[partial_response("TPM-5", name=dispositivo_data.codigo)])

    lugar = LugaresModel.get_one_lugar(db, dispositivo_data.lugarId)
    if not lugar:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(dispositivo_data.lugarId))])

    status_device = StatusDevicesModel.get_one_status(db, dispositivo_data.statusId)
    if not status_device:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(dispositivo_data.statusId))])

    payload = dispositivo_data.model_dump(exclude_none=True)
    payload.pop("lugar", None)
    payload.pop("status", None)
    payload.pop("id", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    try:
        row = DispositivosModel.create_device(db, **payload)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))

    serialized_device = DispositivosSchema.model_validate(row).model_dump(mode="json")
    return fastapi_response([serialized_device], status.HTTP_201_CREATED, "TPM-8")


@router.put("", summary="Actualizar dispositivo")
async def update_dispositivo(
    dispositivo_data: DispositivosSchemaUpdate,
    db: Session = Depends(get_db),
) -> dict:
    if dispositivo_data.id is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    dispositivo_id = int(dispositivo_data.id)
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    payload = dispositivo_data.model_dump(exclude_unset=True, exclude_none=True)
    payload.pop("id", None)
    payload.pop("lugar", None)
    payload.pop("status", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    if "lugarId" in payload:
        lugar = LugaresModel.get_one_lugar(db, payload["lugarId"])
        if not lugar:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(payload["lugarId"]))])

    if "statusId" in payload:
        status_device = StatusDevicesModel.get_one_status(db, payload["statusId"])
        if not status_device:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(payload["statusId"]))])

    try:
        updated = row.update(db, **payload)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))

    serialized = DispositivosSchema.model_validate(updated).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-6")


@router.delete("/{dispositivo_id}", summary="Eliminar dispositivo")
async def delete_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> dict:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    try:
        row.delete(db)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))

    return fastapi_response(None, status.HTTP_200_OK, "TPM-9")


@router.post("/query", summary="Consultar dispositivos")
async def dispositivos_query(
    payload: DispositivosSchemaQuery,
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    filters_payload = payload.model_dump(exclude_none=True)
    if not filters_payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    rows = DispositivosModelSchema.query_devices(db, filters_payload, offset, limit)
    serialized = [DispositivosSchema.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/filter/{value}", summary="Filtrar dispositivos por valor")
async def dispositivos_filter_by_value(
    value: str,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict:
    rows = DispositivosModel.search_by_multiple_fields(db, value, offset, limit)
    if not rows:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = [DispositivosSchema.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("/filterdevice", summary="Filtrar dispositivos")
async def dispositivos_filterdevice(
    payload: dict = Body(...),
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")
    if "value" not in payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="campo Value no encontrado")

    value = str(payload.get("value") or "").strip()
    rows = DispositivosModel.search_by_multiple_fields(db, value, offset, limit)
    if not rows:
        logger.error(f"No devices found with value: '{value}'")
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/filterdeviceFields", summary="Filtrar dispositivos campos- PRINCIPAL QUERY")
@router.post("/filterdeviceFields", summary="Filtrar dispositivos campos")
async def dispositivos_filterdevice_fields(
    offset: int = 0,
    limit: int = 100,
    value: str = "",
    header_value: str | None = Header(default=None, alias="value"),
    db: Session = Depends(get_db),
) -> dict:
    search_value = (header_value or value or "").strip()
    serialized, total_rows = DispositivosModelSchema.filter_fields(
        db,
        offset=offset,
        limit=limit,
        search_value=search_value,
        in_storage=0,
        minimal=False,
    )

    if not serialized:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)


@router.get("/filterdeviceminFields", summary="Filtrar dispositivos minimos")
async def dispositivos_filterdevice_min_fields(
    offset: int = 0,
    limit: int = 100,
    inStorage: int = 0,
    value: str = "",
    header_value: str | None = Header(default=None, alias="value"),
    db: Session = Depends(get_db),
) -> dict:
    search_value = (header_value or value or "").strip()
    serialized, total_rows = DispositivosModelSchema.filter_fields(
        db,
        offset=offset,
        limit=limit,
        search_value=search_value,
        in_storage=inStorage,
        minimal=True,
    )

    if not serialized:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)


@router.get("/filterdeviceByCodigo", summary="Filtrar dispositivos por codigo")
async def dispositivos_filter_by_codigo(
    value: str = Header(default="", alias="value"),
    db: Session = Depends(get_db),
) -> dict:
    logger.info(f"Received filter by codigo request with value: '{value}'")
    row = DispositivosModel.get_devices_by_codigo(db, value)
    if not row:
        logger.error(f"No device found with codigo: '{value}'")
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = DispositivosSchema.model_validate(row).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/alldeviceSomeFields", summary="Listar todos dispositivos campos seleccionados")
async def dispositivos_some_fields(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict:
    serialized, total_rows = DispositivosModelSchema.all_some_fields(db, offset, limit)

    if not serialized:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)


@router.get("/getAmount", summary="Obtener monto total dispositivos")
async def dispositivos_get_amount(db: Session = Depends(get_db)) -> dict:
    rows_count = len(DispositivosModel.get_all_devices(db, offset=0, limit=1))
    if rows_count == 0:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = {"TotalAmount": DispositivosModelSchema.total_amount(db)}
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{dispositivo_id}", summary="Obtener dispositivo por ID")
async def get_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> dict:
    logger.info(f"Received request for device with ID: {dispositivo_id}")
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = DispositivosSchema.model_validate(row).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")
