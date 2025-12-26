# Etat de vie de l'API. Permet de vérifier que l'API est en ligne et fonctionnelle

from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])  # Appartient au groupe "health" dans le swagger.


@router.get("/health")
def health() -> HealthResponse:
    return {"status": "ok"}
