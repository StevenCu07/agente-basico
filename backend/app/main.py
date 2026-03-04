import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="AulaBot API",
        version="1.0.0",
        description="API para agente academico con herramientas de estudio y metricas.",
    )

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_origin, "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_db()
    app.include_router(router, prefix="/api")
    return app


app = create_app()

