import requests
from fastapi import APIRouter, HTTPException

from app.models.schemas import DetectRequest, DetectResponse
from app.services.form_detector import detect_form
from app.services.scraper import fetch_html

router = APIRouter(prefix="/form", tags=["form"])


@router.post("/detect", response_model=DetectResponse)
def detect(request: DetectRequest) -> DetectResponse:
    try:
        status, html = fetch_html(str(request.url))
    except requests.HTTPError as e:
        status_code = getattr(e.response, "status_code", 400)
        raise HTTPException(status_code=status_code, detail=f"HTTP error while fetching page: {e}") from e
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Network error while fetching page: {e}") from e

    result = detect_form(html)

    return DetectResponse(
        url=str(request.url),
        http_status=status,
        has_form=result["has_form"],
        forms_count=result["forms_count"],
        has_inputs=result["has_inputs"],
        probable_form=result["probable_form"],
        reasons=result["reasons"],
    )
