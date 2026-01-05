from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

from app.services.autofiller import fill_fields, make_driver
from app.services.form_analyzer import extract_form_fields
from app.services.user_store import get_user

router = APIRouter(prefix="/form", tags=["form"])


@router.get("/autofill", response_class=HTMLResponse)
def autofill(url: str):
    user = get_user()
    if not user:
        return JSONResponse({"message": "Aucun utilisateur n'est défini"}, status_code=404)

    driver = make_driver()
    try:
        driver.get(url)
        html = driver.page_source

        fields = extract_form_fields(html)
        result = fill_fields(driver, fields, user)

        filled_html = driver.page_source

        debug = (
            f"filled={len(result['filled'])} skipped={len(result['skipped'])} -->\n"
        )
        return HTMLResponse(content=debug + filled_html)

    finally:
        driver.quit()
