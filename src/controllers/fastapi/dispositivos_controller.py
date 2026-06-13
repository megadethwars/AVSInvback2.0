from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.LugaresModel import LugaresModel
from ...models.StatusDevicesModel import StatusDevicesModel
from ...schemas import DispositivosBase, DispositivosCreate, DispositivosUpdate
from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/dispositivos", tags=["Dispositivos"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "", item=None, is_query: bool = False, total: int = 0) -> JSONResponse:
    message_list = []
    if message == "":
        message_list.append({"status": returnCodes.app_codes[app_code]})
    else:
        message_list.append({"status": str(message)})

    if item is None:
        item = []

    if isinstance(item, list):
        for x in item:
            message_list.append(x)
    elif item != "":
        message_list.append({"object": item})

    payload = {
        "app_code": app_code,
        "message": message_list,
        "data": res,
    }
    if is_query:
        payload["total_rows"] = total

    return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar dispositivos")
async def get_dispositivos(
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    rows = DispositivosModel.get_all_devices(db, offset=offset, limit=limit)
    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{dispositivo_id}", summary="Obtener dispositivo por ID")
async def get_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> dict:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = DispositivosBase.model_validate(row).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/search/{search_term}", summary="Buscar dispositivos")
async def search_dispositivos(
    search_term: str,
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    rows = DispositivosModel.search_by_multiple_fields(db, search_term, offset, limit)
    if not rows:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear dispositivo")
async def create_dispositivo(
    dispositivo_data: DispositivosCreate,
    db: Session = Depends(get_db),
) -> dict:
    existing_device = DispositivosModel.get_devices_by_codigo(db, dispositivo_data.codigo)
    if existing_device:
        return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-5", item=dispositivo_data.codigo)

    lugar = LugaresModel.get_one_lugar(db, dispositivo_data.lugarId)
    if not lugar:
        return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=dispositivo_data.lugarId)

    status_device = StatusDevicesModel.get_one_status(db, dispositivo_data.statusId)
    if not status_device:
        return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=dispositivo_data.statusId)

    payload = dispositivo_data.model_dump(exclude_none=True)
    payload.pop("lugar", None)
    payload.pop("status", None)
    payload.pop("id", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    try:
        row = DispositivosModel.create_device(db, **payload)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))

    serialized_device = DispositivosBase.model_validate(row).model_dump(mode="json")
    return _legacy_response([serialized_device], status.HTTP_201_CREATED, "TPM-8")


@router.put("/{dispositivo_id}", summary="Actualizar dispositivo")
async def update_dispositivo(
    dispositivo_id: int,
    dispositivo_data: DispositivosUpdate,
    db: Session = Depends(get_db),
) -> dict:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    payload = dispositivo_data.model_dump(exclude_unset=True, exclude_none=True)
    payload.pop("id", None)
    payload.pop("lugar", None)
    payload.pop("status", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    if "lugarId" in payload:
        lugar = LugaresModel.get_one_lugar(db, payload["lugarId"])
        if not lugar:
            return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=payload["lugarId"])

    if "statusId" in payload:
        status_device = StatusDevicesModel.get_one_status(db, payload["statusId"])
        if not status_device:
            return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=payload["statusId"])

    try:
        updated = row.update(db, **payload)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))

    serialized = DispositivosBase.model_validate(updated).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-6")


@router.delete("/{dispositivo_id}", summary="Eliminar dispositivo")
async def delete_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> dict:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    try:
        row.delete(db)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))

    return _legacy_response(None, status.HTTP_200_OK, "TPM-9")


@router.post("/query", summary="Consultar dispositivos")
async def dispositivos_query() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="dispositivos.query pendiente de migracion")


@router.get("/filter/{value}", summary="Filtrar dispositivos por valor")
async def dispositivos_filter_by_value(value: str) -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message=f"dispositivos.filter({value}) pendiente de migracion")


@router.post("/filterdevice", summary="Filtrar dispositivos")
async def dispositivos_filterdevice() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="dispositivos.filterdevice pendiente de migracion")


@router.post("/filterdeviceFields", summary="Filtrar dispositivos campos")
async def dispositivos_filterdevice_fields() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="dispositivos.filterdeviceFields pendiente de migracion")


@router.get("/filterdeviceminFields", summary="Filtrar dispositivos minimos")
async def dispositivos_filterdevice_min_fields() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="dispositivos.filterdeviceminFields pendiente de migracion")


@router.get("/filterdeviceByCodigo", summary="Filtrar dispositivos por codigo")
async def dispositivos_filter_by_codigo() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="dispositivos.filterdeviceByCodigo pendiente de migracion")


@router.get("/alldeviceSomeFields", summary="Listar dispositivos campos seleccionados")
async def dispositivos_some_fields() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="dispositivos.alldeviceSomeFields pendiente de migracion")


@router.get("/getAmount", summary="Obtener monto total dispositivos")
async def dispositivos_get_amount() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="dispositivos.getAmount pendiente de migracion")
