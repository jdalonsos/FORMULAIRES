# Etat de vie de l'API. Permet de vérifier que l'API est en ligne et fonctionnelle

from fastapi import APIRouter

router = APIRouter(tags=["health"])  # Appartient au groupe "health" dans le swagger.

@router.get("/health")  # noqa: E302
def health() -> dict[str, str]:
    return {"status": "ok"}
