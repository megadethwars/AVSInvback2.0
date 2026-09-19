from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.LugaresModelSchema import LugaresModel, LugaresSchema, LugaresSchemaCreate, LugaresSchemaUpdate
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/lugares", tags=["Lugares"])



@router.get("", summary="Listar todos los lugares")
async def get_lugares(db: Session = Depends(get_db)) -> dict:
    lugares = LugaresModel.get_all_lugares(db)
    serialized = [LugaresSchema.model_validate(item).model_dump(mode="json") for item in lugares]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{item_id}", summary="Obtener lugar por ID")
async def get_lugar(item_id: int, db: Session = Depends(get_db)) -> dict:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = LugaresSchema.model_validate(lugar).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear lugar")
async def create_lugar(lugar_data: LugaresSchemaCreate, db: Session = Depends(get_db)) -> dict:
    try:
        new_lugar = LugaresModel.create_lugar(
            db,
            lugar=lugar_data.lugar,
            activo=lugar_data.activo if lugar_data.activo is not None else True,
        )
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = LugaresSchema.model_validate(new_lugar).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_201_CREATED, "TPM-1")


@router.put("", summary="Actualizar lugar")
async def update_lugar(lugar_data: LugaresSchemaUpdate, db: Session = Depends(get_db)) -> dict:
    if lugar_data.id is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", "id es requerido")

    item_id = int(lugar_data.id)
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_data = lugar_data.model_dump(exclude_unset=True, exclude_none=True)
    update_data.pop("id", None)
    update_data.pop("fechaAlta", None)
    update_data.pop("fechaUltimaModificacion", None)

    try:
        updated_lugar = lugar.update(db, **update_data)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = LugaresSchema.model_validate(updated_lugar).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-6")


@router.delete("/{item_id}", summary="Eliminar lugar")
async def delete_lugar(item_id: int, db: Session = Depends(get_db)) -> dict:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    try:
        lugar.delete(db)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))
    return fastapi_response(None, status.HTTP_200_OK, "TPM-9")
