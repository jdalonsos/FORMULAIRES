from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from app.models.schemas import FormField, UserData
from app.services.field_mapper import match_field_to_user_key

def make_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(25)
    return driver

def _get_user_value(user: UserData, key: str) -> str | None:
    value = getattr(user, key, None)
    if value is None:
        return None
    return str(value)

def _find_element(driver, field: FormField):
    if field.name:
        try:
            return driver.find_element(By.NAME, field.name)
        except NoSuchElementException:
            pass
    if field.id:
        try:
            return driver.find_element(By.ID, field.id)
        except NoSuchElementException:
            pass
    return None

def fill_fields(driver, fields: list[FormField], user: UserData) -> dict:
    filled, skipped = [], []

    for field in fields:
        key, conf, reason = match_field_to_user_key(field)
        if not key:
            skipped.append({"field": field.model_dump(), "reason": reason})
            continue

        value = _get_user_value(user, key)
        if not value:
            skipped.append({"field": field.model_dump(), "reason": f"Pas de données utilisateur pour le champ: {key}"})
            continue

        el = _find_element(driver, field)
        if not el:
            skipped.append({"field": field.model_dump(), "reason": "Element non trouvé"})
            continue

        try:
            el.clear()
        except Exception:
            pass

        el.send_keys(value)

        # On simule un vrai utilisateur qui entrent ses données .
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            el,
        )

        filled.append({"field": field.model_dump(), "key": key, "value": value, "confidence": conf})

    return {"filled": filled, "skipped": skipped}
