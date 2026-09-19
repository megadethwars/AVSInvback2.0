from .lugares_controller import router as lugares_router
from .dispositivos_controller import router as dispositivos_router
from .statusdevices_controller import router as statusdevices_router
from .usuarios_controller import router as usuarios_router
from .movimientos_controller import router as movimientos_router
from .roles_controller import router as roles_router
from .statuslugar_controller import router as statuslugar_router
from .estatususuarios_controller import router as estatususuarios_router
from .tipomovimientos_controller import router as tipomovimientos_router
from .reportes_controller import router as reportes_router
from .jobmovimientos_controller import router as jobmovimientos_router

__all__ = [
    "lugares_router",
    "dispositivos_router",
    "statusdevices_router",
    "usuarios_router",
    "movimientos_router",
    "roles_router",
    "statuslugar_router",
    "estatususuarios_router",
    "tipomovimientos_router",
    "reportes_router",
    "jobmovimientos_router",
]
