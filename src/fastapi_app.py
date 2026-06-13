from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .models.LugaresModel import LugaresModel
from .models.DispositivosModel import DispositivosModel
from .models.StatusDevicesModel import StatusDevicesModel
from .schemas import (
    LugaresBase, LugaresCreate, LugaresUpdate,
    DispositivosBase, DispositivosCreate, DispositivosUpdate,
    StatusDevicesBase, StatusDevicesCreate, StatusDevicesUpdate,
)


def create_app(env_name: str = "local") -> FastAPI:
    app = FastAPI(
        title="Inventory API",
        version="2.0.0",
        description="API REST de gestión de inventario con FastAPI y SQLAlchemy",
        contact={
            "name": "Development Team",
            "email": "dev@example.com",
        },
        license_info={
            "name": "Proprietary",
        },
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize database tables on startup"""
        init_db()
        print("✓ Database initialized")

    # ==================== HEALTH & SYSTEM ====================
    @app.get(
        "/health",
        tags=["System"],
        summary="Health Check",
        description="Verifica el estado de la API y su disponibilidad",
    )
    async def health() -> dict[str, str]:
        """Health check endpoint para monitoreo de disponibilidad."""
        return {"status": "ok"}

    # ==================== LUGARES (UBICACIONES) ====================
    @app.get(
        "/api/v1/lugares",
        response_model=list[LugaresBase],
        tags=["Lugares"],
        summary="Listar todos los lugares",
        description="Obtiene la lista completa de ubicaciones/lugares registrados",
    )
    async def get_lugares(db: Session = Depends(get_db)) -> list[LugaresBase]:
        """Retorna una lista de todos los lugares registrados."""
        lugares = LugaresModel.get_all_lugares(db)
        return [LugaresBase.model_validate(item) for item in lugares]

    @app.get(
        "/api/v1/lugares/{item_id}",
        response_model=LugaresBase,
        tags=["Lugares"],
        summary="Obtener lugar por ID",
        description="Obtiene los detalles de un lugar específico por su identificador",
    )
    async def get_lugar(item_id: int, db: Session = Depends(get_db)) -> LugaresBase:
        """Retorna los detalles de un lugar específico."""
        lugar = LugaresModel.get_one_lugar(db, item_id)
        if not lugar:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TPM-4")
        return LugaresBase.model_validate(lugar)

    @app.post(
        "/api/v1/lugares",
        response_model=LugaresBase,
        tags=["Lugares"],
        summary="Crear nuevo lugar",
        description="Crea una nueva ubicación/lugar en el sistema",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_lugar(
        lugar_data: LugaresCreate, db: Session = Depends(get_db)
    ) -> LugaresBase:
        """Crea un nuevo lugar en la base de datos."""
        new_lugar = LugaresModel.create_lugar(
            db, lugar=lugar_data.lugar, activo=lugar_data.activo if lugar_data.activo is not None else True
        )
        return LugaresBase.model_validate(new_lugar)

    @app.put(
        "/api/v1/lugares/{item_id}",
        response_model=LugaresBase,
        tags=["Lugares"],
        summary="Actualizar lugar",
        description="Actualiza los datos de un lugar existente",
    )
    async def update_lugar(
        item_id: int, lugar_data: LugaresUpdate, db: Session = Depends(get_db)
    ) -> LugaresBase:
        """Actualiza los datos de un lugar existente."""
        lugar = LugaresModel.get_one_lugar(db, item_id)
        if not lugar:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TPM-4")
        
        # Update only provided fields
        update_data = lugar_data.model_dump(exclude_unset=True)
        updated_lugar = lugar.update(db, **update_data)
        return LugaresBase.model_validate(updated_lugar)

    @app.delete(
        "/api/v1/lugares/{item_id}",
        tags=["Lugares"],
        summary="Eliminar lugar",
        description="Elimina un lugar del sistema",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_lugar(item_id: int, db: Session = Depends(get_db)) -> None:
        """Elimina un lugar del sistema."""
        lugar = LugaresModel.get_one_lugar(db, item_id)
        if not lugar:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TPM-4")
        lugar.delete(db)
        return None

    # ==================== STATUS DEVICES ====================
    @app.get(
        "/api/v1/statusDevices",
        response_model=list[StatusDevicesBase],
        tags=["StatusDevices"],
        summary="Listar todos los estatus de dispositivos",
        description="Obtiene la lista completa de estados/estatus de dispositivos",
    )
    async def get_status_devices(db: Session = Depends(get_db)) -> list[StatusDevicesBase]:
        """Retorna una lista de todos los estatus de dispositivos."""
        status_devices = StatusDevicesModel.get_all_status(db)
        return [StatusDevicesBase.model_validate(item) for item in status_devices]

    @app.get(
        "/api/v1/statusDevices/{status_id}",
        response_model=StatusDevicesBase,
        tags=["StatusDevices"],
        summary="Obtener estatus por ID",
        description="Obtiene los detalles de un estatus específico",
    )
    async def get_status_device(status_id: int, db: Session = Depends(get_db)) -> StatusDevicesBase:
        """Retorna los detalles de un estatus específico."""
        status_device = StatusDevicesModel.get_one_status(db, status_id)
        if not status_device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
        return StatusDevicesBase.model_validate(status_device)

    @app.post(
        "/api/v1/statusDevices",
        response_model=StatusDevicesBase,
        tags=["StatusDevices"],
        summary="Crear nuevo estatus",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_status_device(
        status_data: StatusDevicesCreate, db: Session = Depends(get_db)
    ) -> StatusDevicesBase:
        """Crea un nuevo estatus de dispositivo."""
        new_status = StatusDevicesModel.create_status(db, descripcion=status_data.descripcion)
        return StatusDevicesBase.model_validate(new_status)

    @app.put(
        "/api/v1/statusDevices/{status_id}",
        response_model=StatusDevicesBase,
        tags=["StatusDevices"],
        summary="Actualizar estatus",
    )
    async def update_status_device(
        status_id: int, status_data: StatusDevicesUpdate, db: Session = Depends(get_db)
    ) -> StatusDevicesBase:
        """Actualiza un estatus de dispositivo."""
        status_device = StatusDevicesModel.get_one_status(db, status_id)
        if not status_device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
        
        update_data = status_data.model_dump(exclude_unset=True)
        updated_status = status_device.update(db, **update_data)
        return StatusDevicesBase.model_validate(updated_status)

    @app.delete(
        "/api/v1/statusDevices/{status_id}",
        tags=["StatusDevices"],
        summary="Eliminar estatus",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_status_device(status_id: int, db: Session = Depends(get_db)) -> None:
        """Elimina un estatus de dispositivo."""
        status_device = StatusDevicesModel.get_one_status(db, status_id)
        if not status_device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
        status_device.delete(db)
        return None

    # ==================== DISPOSITIVOS ====================
    @app.get(
        "/api/v1/dispositivos",
        response_model=list[DispositivosBase],
        tags=["Dispositivos"],
        summary="Listar todos los dispositivos",
        description="Obtiene la lista completa de dispositivos",
    )
    async def get_dispositivos(
        offset: int = 0, limit: int = 10, db: Session = Depends(get_db)
    ) -> list[DispositivosBase]:
        """Retorna una lista paginada de dispositivos."""
        dispositivos = DispositivosModel.get_all_devices(db, offset=offset, limit=limit)
        return [DispositivosBase.model_validate(item) for item in dispositivos]

    @app.get(
        "/api/v1/dispositivos/{dispositivo_id}",
        response_model=DispositivosBase,
        tags=["Dispositivos"],
        summary="Obtener dispositivo por ID",
        description="Obtiene los detalles de un dispositivo específico",
    )
    async def get_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> DispositivosBase:
        """Retorna los detalles de un dispositivo específico."""
        dispositivo = DispositivosModel.get_one_device(db, dispositivo_id)
        if not dispositivo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        return DispositivosBase.model_validate(dispositivo)

    @app.get(
        "/api/v1/dispositivos/search/{search_term}",
        response_model=list[DispositivosBase],
        tags=["Dispositivos"],
        summary="Buscar dispositivos",
        description="Busca dispositivos por múltiples campos",
    )
    async def search_dispositivos(
        search_term: str, offset: int = 0, limit: int = 10, db: Session = Depends(get_db)
    ) -> list[DispositivosBase]:
        """Busca dispositivos por término en múltiples campos."""
        dispositivos = DispositivosModel.search_by_multiple_fields(db, search_term, offset, limit)
        return [DispositivosBase.model_validate(item) for item in dispositivos]

    @app.post(
        "/api/v1/dispositivos",
        response_model=DispositivosBase,
        tags=["Dispositivos"],
        summary="Crear nuevo dispositivo",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_dispositivo(
        dispositivo_data: DispositivosCreate, db: Session = Depends(get_db)
    ) -> DispositivosBase:
        """Crea un nuevo dispositivo en el sistema."""
        # Validate that lugar and status exist
        lugar = LugaresModel.get_one_lugar(db, dispositivo_data.lugarId)
        if not lugar:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid lugarId")
        
        status_device = StatusDevicesModel.get_one_status(db, dispositivo_data.statusId)
        if not status_device:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid statusId")

        payload = dispositivo_data.model_dump(exclude_none=True)
        payload.pop("lugar", None)
        payload.pop("status", None)
        payload.pop("id", None)
        payload.pop("fechaAlta", None)
        payload.pop("fechaUltimaModificacion", None)

        new_dispositivo = DispositivosModel.create_device(db, **payload)
        return DispositivosBase.model_validate(new_dispositivo)

    @app.put(
        "/api/v1/dispositivos/{dispositivo_id}",
        response_model=DispositivosBase,
        tags=["Dispositivos"],
        summary="Actualizar dispositivo",
    )
    async def update_dispositivo(
        dispositivo_id: int, dispositivo_data: DispositivosUpdate, db: Session = Depends(get_db)
    ) -> DispositivosBase:
        """Actualiza un dispositivo existente."""
        dispositivo = DispositivosModel.get_one_device(db, dispositivo_id)
        if not dispositivo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        
        update_data = dispositivo_data.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("id", None)
        update_data.pop("lugar", None)
        update_data.pop("status", None)
        update_data.pop("fechaAlta", None)
        update_data.pop("fechaUltimaModificacion", None)

        if "lugarId" in update_data:
            lugar = LugaresModel.get_one_lugar(db, update_data["lugarId"])
            if not lugar:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid lugarId")

        if "statusId" in update_data:
            status_device = StatusDevicesModel.get_one_status(db, update_data["statusId"])
            if not status_device:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid statusId")

        updated_dispositivo = dispositivo.update(db, **update_data)
        return DispositivosBase.model_validate(updated_dispositivo)

    @app.delete(
        "/api/v1/dispositivos/{dispositivo_id}",
        tags=["Dispositivos"],
        summary="Eliminar dispositivo",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> None:
        """Elimina un dispositivo del sistema."""
        dispositivo = DispositivosModel.get_one_device(db, dispositivo_id)
        if not dispositivo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        dispositivo.delete(db)
        return None

    return app


# Create app instance
app = create_app("local")