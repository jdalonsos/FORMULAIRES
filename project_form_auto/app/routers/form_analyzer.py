import requests
from fastapi import APIRouter, HTTPException

from app.models.schemas import DetectRequest, FormAnalyzeResponse
from app.services.form_analyzer import extract_form_fields
from app.services.scraper import fetch_html

router = APIRouter(prefix="/form", tags=["form"])

@router.post("/analyze", response_model=FormAnalyzeResponse)
def analyze_form(request: DetectRequest) -> FormAnalyzeResponse:
    """
    Analyze a given URL and extract user‑fillable form fields.

    This endpoint fetches the HTML of the provided URL using the scraper
    service. If the fetch fails, a 502 HTTP error is returned. Once the HTML is
    retrieved, the form analyzer service extracts fields such as inputs,
    textareas and selects that are likely to be filled by a user. It
    constructs a ``FormAnalyzeResponse`` containing the original URL, a count
    of the discovered fields, and the list of extracted fields.
    """
    try:
        _, html = fetch_html(str(request.url))
    except requests.RequestException as e:
        # Surface network errors as a 502 Bad Gateway so clients can distinguish
        # between invalid URLs and server issues.
        raise HTTPException(status_code=502, detail=str(e)) from e

    # Delegate HTML parsing and field extraction to the form analyzer service.
    fields = extract_form_fields(html)

    return FormAnalyzeResponse(
        url=str(request.url),
        fields_count=len(fields),
        fields=fields,
    )
