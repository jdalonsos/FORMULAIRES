from fastapi import FastAPI

from app.routers.health import router as health_router

app = FastAPI(title="Web Form Detector", version="0.1.0")

app.include_router(health_router)
