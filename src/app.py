from fastapi import FastAPI
from .routes.api import router as api_router
from .routes.health import router as health_router

app = FastAPI()
app.include_router(router=api_router, prefix="/api")
app.include_router(router=health_router)
