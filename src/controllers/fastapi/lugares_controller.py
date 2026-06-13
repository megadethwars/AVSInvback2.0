from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.LugaresModel import LugaresModel
from ...schemas import LugaresBase, LugaresCreate, LugaresUpdate

router = APIRouter(prefix="/api/v1/lugares", tags=["Lugares"])


@router.get("", response_model=list[LugaresBase], summary="Listar todos los lugares")
async def get_lugares(db: Session = Depends(get_db)) -> list[LugaresBase]:
    lugares = LugaresModel.get_all_lugares(db)
    return [LugaresBase.model_validate(item) for item in lugares]


@router.get("/{item_id}", response_model=LugaresBase, summary="Obtener lugar por ID")
async def get_lugar(item_id: int, db: Session = Depends(get_db)) -> LugaresBase:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TPM-4")
    return LugaresBase.model_validate(lugar)


@router.post("", response_model=LugaresBase, status_code=status.HTTP_201_CREATED, summary="Crear lugar")
async def create_lugar(lugar_data: LugaresCreate, db: Session = Depends(get_db)) -> LugaresBase:
    new_lugar = LugaresModel.create_lugar(
        db,
        lugar=lugar_data.lugar,
        activo=lugar_data.activo if lugar_data.activo is not None else True,
    )
    return LugaresBase.model_validate(new_lugar)


@router.put("/{item_id}", response_model=LugaresBase, summary="Actualizar lugar")
async def update_lugar(item_id: int, lugar_data: LugaresUpdate, db: Session = Depends(get_db)) -> LugaresBase:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TPM-4")

    update_data = lugar_data.model_dump(exclude_unset=True, exclude_none=True)
    update_data.pop("id", None)
    update_data.pop("fechaAlta", None)
    update_data.pop("fechaUltimaModificacion", None)

    updated_lugar = lugar.update(db, **update_data)
    return LugaresBase.model_validate(updated_lugar)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar lugar")
async def delete_lugar(item_id: int, db: Session = Depends(get_db)) -> None:
    lugar = LugaresModel.get_one_lugar(db, item_id)
    if not lugar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TPM-4")
    lugar.delete(db)
    return None
