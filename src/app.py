from fastapi import FastAPI
from .routes.api import router as api_router

app = FastAPI()
app.include_router(router=api_router)
