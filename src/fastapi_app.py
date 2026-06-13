from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .models.LugaresModel import LugaresModel
from .schemas import LugaresBase, LugaresCreate, LugaresUpdate


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

    return app


# Create app instance
app = create_app("local")