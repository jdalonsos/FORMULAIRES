from fastapi import FastAPI
from app.routers.form_analyzer import router as form_analyze_router
from app.routers.form_detect import router as form_detect_router
from app.routers.health import router as health_router

app = FastAPI(title="Web Form Detector", version="0.1.0")

app.include_router(health_router)
app.include_router(form_detect_router)
app.include_router(form_analyze_router)