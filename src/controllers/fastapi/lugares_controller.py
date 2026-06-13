from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.LugaresModel import LugaresModel
from ...schemas import LugaresBase, LugaresCreate, LugaresUpdate
from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/lugares", tags=["Lugares"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
    payload = {
        "app_code": app_code,
        "message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
        "data": res,
    }
    return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar todos los lugares")
async def get_lugares(db: Session = Depends(get_db)) -> dict:
    lugares = LugaresModel.get_all_lugares(db)
    serialized = [LugaresBase.model_validate(item).model_dump(mode="json") for item in lugares]
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{item_id}", summary="Obtener lugar por ID")
async def get_lugar(item_id: int, db: Session = Depends(get_db)) -> dict:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = LugaresBase.model_validate(lugar).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear lugar")
async def create_lugar(lugar_data: LugaresCreate, db: Session = Depends(get_db)) -> dict:
    try:
        new_lugar = LugaresModel.create_lugar(
            db,
            lugar=lugar_data.lugar,
            activo=lugar_data.activo if lugar_data.activo is not None else True,
        )
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = LugaresBase.model_validate(new_lugar).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_201_CREATED, "TPM-1")


@router.put("/{item_id}", summary="Actualizar lugar")
async def update_lugar(item_id: int, lugar_data: LugaresUpdate, db: Session = Depends(get_db)) -> dict:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_data = lugar_data.model_dump(exclude_unset=True, exclude_none=True)
    update_data.pop("id", None)
    update_data.pop("fechaAlta", None)
    update_data.pop("fechaUltimaModificacion", None)

    try:
        updated_lugar = lugar.update(db, **update_data)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = LugaresBase.model_validate(updated_lugar).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-6")


@router.delete("/{item_id}", summary="Eliminar lugar")
async def delete_lugar(item_id: int, db: Session = Depends(get_db)) -> dict:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    try:
        lugar.delete(db)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))
    return _legacy_response(None, status.HTTP_200_OK, "TPM-9")
