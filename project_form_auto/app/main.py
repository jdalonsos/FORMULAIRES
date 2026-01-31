from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.autofill import router as autofill_router
from app.routers.form_analyzer import router as form_analyze_router
from app.routers.form_detect import router as form_detect_router
from app.routers.form_map import router as form_map_router
from app.routers.health import router as health_router
from app.routers.user_data import router as user_router

app = FastAPI(title="Web Form Detector", version="0.1.0")

# CORS pour permettre l'extension de communiquer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En dev, autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(user_router)
app.include_router(form_detect_router)
app.include_router(form_analyze_router)
app.include_router(form_map_router)
app.include_router(autofill_router)
