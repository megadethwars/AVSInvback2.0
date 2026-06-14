from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .controllers.fastapi import (
    lugares_router,
    dispositivos_router,
    statusdevices_router,
    usuarios_router,
    movimientos_router,
    roles_router,
    statuslugar_router,
    estatususuarios_router,
    tipomovimientos_router,
    reportes_router,
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

    @app.get("/health", tags=["System"], summary="Health Check")
    async def health() -> dict[str, str]:

        print("[INFO] Health check endpoint called")
        return {"status": "ok"}

    app.include_router(lugares_router)
    app.include_router(dispositivos_router)
    app.include_router(statusdevices_router)
    app.include_router(usuarios_router)
    app.include_router(movimientos_router)
    app.include_router(roles_router)
    app.include_router(statuslugar_router)
    app.include_router(estatususuarios_router)
    app.include_router(tipomovimientos_router)
    app.include_router(reportes_router)

    return app


# Create app instance
app = create_app("local")