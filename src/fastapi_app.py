from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.wsgi import WSGIMiddleware

from .appinit import create_app as create_flask_app
from .models.LugaresModel import LugaresModel
from .schemas import LugaresBase, LugaresCreate, LugaresUpdate


def create_app(env_name: str = "local") -> FastAPI:
    app = FastAPI(
        title="Inventory API",
        version="2.0.0",
        description="API REST de gestión de inventario migrada de Flask a FastAPI con Pydantic",
        contact={
            "name": "Development Team",
            "email": "dev@example.com",
        },
        license_info={
            "name": "Proprietary",
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==================== HEALTH & SYSTEM ====================
    @app.get(
        "/health",
        tags=["System"],
        summary="Health Check",
        description="Verifica el estado de la API y su disponibilidad",
        responses={
            200: {
                "description": "API está funcionando correctamente",
                "content": {
                    "application/json": {
                        "example": {"status": "ok"}
                    }
                },
            }
        },
    )
    async def health() -> dict[str, str]:
        """
        Health check endpoint para monitoreo de disponibilidad.
        
        Retorna:
        - status: "ok" si la API está disponible
        """
        return {"status": "ok"}

    # ==================== LUGARES (UBICACIONES) ====================
    @app.get(
        "/api/v1/lugares",
        response_model=list[LugaresBase],
        tags=["Lugares"],
        summary="Listar todos los lugares",
        description="Obtiene la lista completa de ubicaciones/lugares registrados en el sistema",
        responses={
            200: {
                "description": "Lista de lugares obtenida exitosamente",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "id": 1,
                                "lugar": "Almacén Principal",
                                "fechaAlta": "2024-01-15T10:30:00",
                                "fechaUltimaModificacion": "2024-06-10T14:20:00",
                                "activo": True,
                            },
                            {
                                "id": 2,
                                "lugar": "Oficina Central",
                                "fechaAlta": "2024-02-20T09:15:00",
                                "fechaUltimaModificacion": "2024-06-12T11:45:00",
                                "activo": True,
                            },
                        ]
                    }
                },
            },
            500: {"description": "Error interno del servidor"},
        },
    )
    async def get_lugares() -> list[LugaresBase]:
        """
        Retorna una lista de todos los lugares registrados.
        
        Cada lugar incluye:
        - id: Identificador único
        - lugar: Nombre/descripción del lugar
        - fechaAlta: Fecha de creación
        - fechaUltimaModificacion: Última actualización
        - activo: Estado del registro
        """
        lugares = LugaresModel.get_all_lugares()
        return [LugaresBase.model_validate(item) for item in lugares]

    @app.get(
        "/api/v1/lugares/{item_id}",
        response_model=LugaresBase,
        tags=["Lugares"],
        summary="Obtener lugar por ID",
        description="Obtiene los detalles de un lugar específico por su identificador",
        responses={
            200: {
                "description": "Lugar encontrado exitosamente",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "lugar": "Almacén Principal",
                            "fechaAlta": "2024-01-15T10:30:00",
                            "fechaUltimaModificacion": "2024-06-10T14:20:00",
                            "activo": True,
                        }
                    }
                },
            },
            404: {
                "description": "Lugar no encontrado (Código: TPM-4)",
                "content": {
                    "application/json": {
                        "example": {"detail": "TPM-4"}
                    }
                },
            },
            500: {"description": "Error interno del servidor"},
        },
    )
    async def get_lugar(item_id: int) -> LugaresBase:
        """
        Retorna los detalles de un lugar específico.
        
        Parámetros:
        - item_id: ID del lugar a consultar
        
        Raises:
        - HTTPException 404: Si el lugar no existe (TPM-4)
        """
        lugar = LugaresModel.get_one_lugar(item_id)
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
        responses={
            201: {
                "description": "Lugar creado exitosamente",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 3,
                            "lugar": "Nuevo Almacén",
                            "fechaAlta": "2024-06-13T10:30:00",
                            "fechaUltimaModificacion": "2024-06-13T10:30:00",
                            "activo": True,
                        }
                    }
                },
            },
            400: {"description": "Datos inválidos"},
            500: {"description": "Error interno del servidor"},
        },
    )
    async def create_lugar(lugar_data: LugaresCreate) -> LugaresBase:
        """
        Crea un nuevo lugar en la base de datos.
        
        Parámetros:
        - lugar: Nombre del lugar (requerido, máx 100 caracteres)
        
        Retorna:
        - El lugar creado con ID asignado
        """
        # TODO: Implementar lógica de creación
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint en desarrollo",
        )

    @app.put(
        "/api/v1/lugares/{item_id}",
        response_model=LugaresBase,
        tags=["Lugares"],
        summary="Actualizar lugar",
        description="Actualiza los datos de un lugar existente",
        responses={
            200: {"description": "Lugar actualizado exitosamente"},
            404: {"description": "Lugar no encontrado"},
            400: {"description": "Datos inválidos"},
            500: {"description": "Error interno del servidor"},
        },
    )
    async def update_lugar(item_id: int, lugar_data: LugaresUpdate) -> LugaresBase:
        """
        Actualiza los datos de un lugar existente.
        
        Parámetros:
        - item_id: ID del lugar a actualizar
        - lugar_data: Datos a actualizar
        
        Retorna:
        - El lugar actualizado
        """
        # TODO: Implementar lógica de actualización
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint en desarrollo",
        )

    @app.delete(
        "/api/v1/lugares/{item_id}",
        tags=["Lugares"],
        summary="Eliminar lugar",
        description="Elimina un lugar del sistema",
        responses={
            204: {"description": "Lugar eliminado exitosamente"},
            404: {"description": "Lugar no encontrado"},
            500: {"description": "Error interno del servidor"},
        },
    )
    async def delete_lugar(item_id: int) -> dict:
        """
        Elimina un lugar del sistema.
        
        Parámetros:
        - item_id: ID del lugar a eliminar
        """
        # TODO: Implementar lógica de eliminación
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint en desarrollo",
        )

    flask_app = create_flask_app(env_name)
    app.mount("/", WSGIMiddleware(flask_app))

    return app


app = create_app("local")