import requests
from fastapi import APIRouter, HTTPException

from app.models.schemas import DetectRequest, FormAnalyzeResponse
from app.services.form_analyzer import extract_form_fields
from app.services.scraper import fetch_html

router = APIRouter(prefix="/form", tags=["form"])


@router.post("/analyze", response_model=FormAnalyzeResponse)
def analyze_form(request: DetectRequest) -> FormAnalyzeResponse:
    try:
        _, html = fetch_html(str(request.url))
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    fields = extract_form_fields(html)

    return FormAnalyzeResponse(
        url=str(request.url),
        fields_count=len(fields),
        fields=fields,
    )
