import requests
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    FormMapRequest,
    FormMapResponse,
    MappedFormField,
)
from app.services.field_mapper import match_field_to_user_key
from app.services.form_analyzer import extract_form_fields
from app.services.scraper import fetch_html

router = APIRouter(prefix="/form", tags=["form"])


@router.post("/map", response_model=FormMapResponse)
def map_form_fields(req: FormMapRequest) -> FormMapResponse:
    try:
        _, html = fetch_html(req.url)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    fields = extract_form_fields(html)

    mapped_fields: list[MappedFormField] = []

    for field in fields:
        matched_key, confidence, reason = match_field_to_user_key(field)

        mapped_fields.append(
            MappedFormField(
                tag=field.tag,
                type=field.type,
                name=field.name,
                id=field.id,
                placeholder=field.placeholder,
                label=field.label,
                matched_key=matched_key,
                confidence=confidence,
                reason=reason,
            )
        )

    matched_count = sum(1 for f in mapped_fields if f.matched_key)

    return FormMapResponse(
        url=req.url,
        total_fields=len(mapped_fields),
        matched_fields=matched_count,
        fields=mapped_fields,
    )
