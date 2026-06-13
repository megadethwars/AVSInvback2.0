from fastapi import APIRouter, Body, Depends, Header, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.LugaresModel import LugaresModel
from ...models.StatusDevicesModel import StatusDevicesModel
from ...schemas import DispositivosBase, DispositivosCreate, DispositivosQuery, DispositivosUpdate
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/dispositivos", tags=["Dispositivos"])


def _serialize_some_fields(device: DispositivosModel) -> dict:
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


def _serialize_min_fields(device: DispositivosModel) -> dict:
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


@router.get("", summary="Listar dispositivos")
async def get_dispositivos(
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    rows = DispositivosModel.get_all_devices(db, offset=offset, limit=limit)
    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
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
    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear dispositivo")
async def create_dispositivo(
    dispositivo_data: DispositivosCreate,
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

    serialized_device = DispositivosBase.model_validate(row).model_dump(mode="json")
    return fastapi_response([serialized_device], status.HTTP_201_CREATED, "TPM-8")


@router.put("", summary="Actualizar dispositivo")
async def update_dispositivo(
    dispositivo_data: DispositivosUpdate,
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

    serialized = DispositivosBase.model_validate(updated).model_dump(mode="json")
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
    payload: DispositivosQuery,
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    filters_payload = payload.model_dump(exclude_none=True)
    if not filters_payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    base_query = select(DispositivosModel)

    for field_name, field_value in filters_payload.items():
        if not hasattr(DispositivosModel, field_name):
            continue
        column = getattr(DispositivosModel, field_name)
        if isinstance(field_value, str):
            base_query = base_query.where(column.ilike(f"%{field_value}%"))
        else:
            base_query = base_query.where(column == field_value)

    rows = db.execute(
        base_query
        .order_by(DispositivosModel.producto)
        .offset(offset)
        .limit(limit)
    ).scalars().all()
    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
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

    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
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
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = [DispositivosBase.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/filterdeviceFields", summary="Filtrar dispositivos campos")
@router.post("/filterdeviceFields", summary="Filtrar dispositivos campos")
async def dispositivos_filterdevice_fields(
    offset: int = 0,
    limit: int = 100,
    value: str = "",
    header_value: str | None = Header(default=None, alias="value"),
    db: Session = Depends(get_db),
) -> dict:
    search_value = (header_value or value or "").strip()
    base_query = select(DispositivosModel)
    count_query = select(func.count()).select_from(DispositivosModel)

    if search_value:
        pattern = f"%{search_value}%"
        filters = or_(
            DispositivosModel.codigo.ilike(pattern),
            DispositivosModel.producto.ilike(pattern),
            DispositivosModel.marca.ilike(pattern),
            DispositivosModel.modelo.ilike(pattern),
            DispositivosModel.serie.ilike(pattern),
            DispositivosModel.accesorios.ilike(pattern),
        )
        base_query = base_query.where(filters)
        count_query = count_query.where(filters)

    total_rows = int(db.execute(count_query).scalar() or 0)
    rows = db.execute(
        base_query
        .order_by(DispositivosModel.producto)
        .offset(offset)
        .limit(limit)
    ).scalars().all()

    if not rows:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = [_serialize_some_fields(row) for row in rows]
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
    base_query = select(DispositivosModel)
    count_query = select(func.count()).select_from(DispositivosModel)

    if search_value:
        pattern = f"%{search_value}%"
        filters = or_(
            DispositivosModel.codigo.ilike(pattern),
            DispositivosModel.producto.ilike(pattern),
            DispositivosModel.marca.ilike(pattern),
            DispositivosModel.modelo.ilike(pattern),
            DispositivosModel.serie.ilike(pattern),
        )
        base_query = base_query.where(filters)
        count_query = count_query.where(filters)

    if int(inStorage) == 1:
        base_query = base_query.where(DispositivosModel.cantidad > 0)
        count_query = count_query.where(DispositivosModel.cantidad > 0)

    total_rows = int(db.execute(count_query).scalar() or 0)
    rows = db.execute(
        base_query
        .order_by(DispositivosModel.producto)
        .offset(offset)
        .limit(limit)
    ).scalars().all()

    if not rows:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = [_serialize_min_fields(row) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)


@router.get("/filterdeviceByCodigo", summary="Filtrar dispositivos por codigo")
async def dispositivos_filter_by_codigo(
    value: str = Header(default="", alias="value"),
    db: Session = Depends(get_db),
) -> dict:
    row = DispositivosModel.get_devices_by_codigo(db, value)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = DispositivosBase.model_validate(row).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/alldeviceSomeFields", summary="Listar dispositivos campos seleccionados")
async def dispositivos_some_fields(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict:
    total_rows = int(db.execute(select(func.count()).select_from(DispositivosModel)).scalar() or 0)
    rows = db.execute(
        select(DispositivosModel)
        .order_by(DispositivosModel.producto)
        .offset(offset)
        .limit(limit)
    ).scalars().all()

    if not rows:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    serialized = [_serialize_some_fields(row) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)


@router.get("/getAmount", summary="Obtener monto total dispositivos")
async def dispositivos_get_amount(db: Session = Depends(get_db)) -> dict:
    rows_count = int(db.execute(select(func.count()).select_from(DispositivosModel)).scalar() or 0)
    if rows_count == 0:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    total_amount = db.execute(
        select(func.coalesce(func.sum(func.coalesce(DispositivosModel.costo, 0) * func.coalesce(DispositivosModel.cantidad, 0)), 0))
    ).scalar()

    serialized = {"TotalAmount": float(total_amount or 0)}
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{dispositivo_id}", summary="Obtener dispositivo por ID")
async def get_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> dict:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = DispositivosBase.model_validate(row).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")
