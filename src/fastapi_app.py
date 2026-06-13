from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware

from .appinit import create_app as create_flask_app
from .models.LugaresModel import LugaresModel
from .schemas import LugaresBase


def create_app(env_name: str = "local") -> FastAPI:
    app = FastAPI(title="Inventory API", version="1.1", description="Inventory API migrated to FastAPI")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/lugares", response_model=list[LugaresBase])
    async def get_lugares() -> list[LugaresBase]:
        lugares = LugaresModel.get_all_lugares()
        return [LugaresBase.model_validate(item) for item in lugares]

    @app.get("/api/v1/lugares/{item_id}", response_model=LugaresBase)
    async def get_lugar(item_id: int) -> LugaresBase:
        lugar = LugaresModel.get_one_lugar(item_id)
        if not lugar:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="TPM-4")

        return LugaresBase.model_validate(lugar)

    flask_app = create_flask_app(env_name)
    app.mount("/", WSGIMiddleware(flask_app))

    return app


app = create_app("local")