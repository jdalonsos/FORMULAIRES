"""API router for automatic form filling.

This router exposes an endpoint that accepts a URL and a set of user data
attributes, then attempts to locate and fill any user‑fillable form fields
found on the page. The response includes details about each field and whether
it was successfully filled.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import AutoFillRequest, AutoFillResponse
from app.services.autofiller import autofill_form


router = APIRouter(prefix="/form", tags=["form"])


@router.post("/autofill", response_model=AutoFillResponse)
def autofill_endpoint(req: AutoFillRequest) -> AutoFillResponse:
    """
    Attempt to automatically fill form fields on the specified page.

    Parameters
    ----------
    req: AutoFillRequest
        Contains the target URL and a ``UserData`` instance with personal
        information. Fields within forms on the page are matched to keys on
        ``user_data`` based on heuristics in the field mapper. When a match is
        found the corresponding value is entered into the field using a
        headless browser.

    Returns
    -------
    AutoFillResponse
        A response containing statistics about the number of fields found and
        filled, along with detailed information for each field encountered.
    """
    try:
        fields = autofill_form(req.url, req.user_data)
    except Exception as e:
        # Wrap any exception from the automation layer in a 502 so clients
        # understand the request was valid but the upstream service failed.
        raise HTTPException(status_code=502, detail=str(e)) from e

    total = len(fields)
    filled = sum(1 for f in fields if f.filled)
    return AutoFillResponse(
        url=req.url,
        total_fields=total,
        filled_fields=filled,
        fields=fields,
    )
