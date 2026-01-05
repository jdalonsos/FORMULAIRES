"""Utilities to automatically fill web forms with user data.

This module provides a single high‑level function, :func:`autofill_form`, which
uses Selenium in headless mode to load a page, locate form fields and fill
them with values from a ``UserData`` instance. Field matching relies on the
same heuristics used by the ``field_mapper`` service. After completion the
browser is closed and a list of :class:`AutofilledField` objects is returned
describing how each field was handled.
"""

from __future__ import annotations

from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException, TimeoutException

from app.models.schemas import UserData, FormField, AutofilledField
from app.services.scraper import create_driver
from app.services.field_mapper import match_field_to_user_key


def _build_field(element) -> FormField:
    """Construct a ``FormField`` model from a Selenium WebElement.

    Selenium does not provide labels directly; only attributes on the
    element can be inspected. The label will therefore be left as ``None``
    during auto‑filling.
    """
    return FormField(
        tag=element.tag_name,
        type=element.get_attribute("type"),
        name=element.get_attribute("name"),
        id=element.get_attribute("id"),
        placeholder=element.get_attribute("placeholder"),
        label=None,
    )


def _fill_input(element, value: str) -> bool:
    """Attempt to fill a generic input or textarea element.

    Returns ``True`` if the operation succeeded without raising an exception.
    """
    try:
        # Attempt to clear existing content if the element supports it.
        try:
            element.clear()
        except Exception:
            pass
        element.send_keys(value)
        return True
    except Exception:
        return False


def _fill_select(element, value: str) -> bool:
    """Attempt to select an option in a ``<select>`` element matching ``value``.

    The search is case‑insensitive and will compare both the option value and
    visible text. Returns ``True`` on success.
    """
    try:
        select = Select(element)
    except Exception:
        return False

    value_lower = value.lower()
    for option in select.options:
        opt_value = option.get_attribute("value") or ""
        opt_text = option.text or ""
        if opt_value.lower() == value_lower:
            select.select_by_value(opt_value)
            return True
        if opt_text.lower() == value_lower:
            select.select_by_visible_text(option.text)
            return True
    return False


def _accept_cookie_banner(driver) -> bool:
    """Try to dismiss cookie consent pop‑ups by clicking a consent button.

    Many websites present a cookie consent banner or modal that blocks user
    interaction until cookies are accepted.  According to best practices,
    clicking the consent button is preferred over removing the element so that
    any associated behaviour (e.g. setting a cookie) is preserved【648687675336126†L247-L303】.  This helper
    function scans the page for clickable `<button>` elements whose text
    contains common consent keywords (both English and French) such as
    “accept”, “agree”, “accepter”, “j'accepte”, “consent”, “oui” or “ok”.  If
    a matching button is found it is clicked; otherwise the function returns
    ``False``.  Any exceptions are silently ignored to avoid interrupting the
    auto‑fill workflow.

    Parameters
    ----------
    driver
        A Selenium WebDriver instance pointing to the current page.

    Returns
    -------
    bool
        ``True`` if a consent button was clicked, ``False`` otherwise.
    """
    # Define keywords in lower case for matching
    keywords = [
        "accept",
        "agree",
        "accepter",
        "j'accepte",
        "consent",
        "ok",
        "oui",
    ]
    try:
        # Wait briefly for any modal or banner to appear
        WebDriverWait(driver, 2).until(lambda d: True)
        buttons = driver.find_elements(By.XPATH, "//button")
        for btn in buttons:
            text = (btn.text or "").strip().lower()
            # Some banners use `<span>` inside buttons; fallback to aria-label
            aria = (btn.get_attribute("aria-label") or "").strip().lower()
            combined = text + " " + aria
            if any(kw in combined for kw in keywords):
                try:
                    btn.click()
                    return True
                except Exception:
                    continue
    except Exception:
        pass
    return False


def autofill_form(
    url: str,
    user_data: UserData,
    wait_seconds: int = 10,
    *,
    close_driver: bool = True,
) -> list[AutofilledField] | tuple[list[AutofilledField], any]:
    """
    Fill as many user‑fillable fields on the given page as possible.

    A headless Chrome browser is created, navigates to ``url`` and waits
    until the page's ``<body>`` element is present. All input, textarea and
    select elements are then inspected. Each field is passed through the
    matcher to infer which ``user_data`` attribute may correspond to it. When
    a match is found and the user has provided a non‑empty value for that
    attribute, the value is entered into the DOM element using Selenium.

    If an element cannot be filled (e.g. due to type constraints or unexpected
    exceptions) the field is still returned but marked as ``filled=False``.

    Parameters
    ----------
    url: str
        The absolute or relative URL of the web page containing the form.
    user_data: UserData
        An instance of ``UserData`` with candidate values to insert into the
        form fields.
    wait_seconds: int, optional
        Maximum number of seconds to wait for the page to load. Defaults
        to 10.
    close_driver: bool, optional
        Whether to close the Selenium WebDriver at the end of the call. If
        ``True`` (the default), the browser instance is quit and only the
        list of autofilled fields is returned. If ``False``, the driver
        remains open and the return value is a 2‑tuple ``(fields, driver)``.

    Returns
    -------
    List[AutofilledField] or (List[AutofilledField], WebDriver)
        If ``close_driver`` is ``True``, returns just the list of
        ``AutofilledField`` records describing how each element was
        handled. If ``close_driver`` is ``False``, returns a tuple of the
        field list and the still‑running WebDriver instance. In both cases
        the list order corresponds to the DOM order of the inspected
        elements.
    """
    # Always create a new browser instance. When ``close_driver`` is False the
    # caller is responsible for cleaning up the returned driver.  The return
    # type is either just the list of :class:`AutofilledField` records (the
    # historical behaviour) or a tuple ``(fields, driver)`` when
    # ``close_driver`` is ``False``.
    driver = create_driver()
    fields: list[AutofilledField] = []
    try:
        # Navigate to the page and wait until the body is present
        driver.get(url)
        # Wait for the body to ensure page is loaded
        WebDriverWait(driver, wait_seconds).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Handle common cookie consent pop‑ups by attempting to click an
        # “accept cookies” button. Many sites display a modal or banner on
        # initial load that blocks interaction until cookies are accepted.  We
        # search for buttons containing typical consent keywords and click the
        # first match.  If none is found within a short timeout, we continue
        # without raising an error.
        _accept_cookie_banner(driver)

        # Gather all input-like elements in the main document
        elements = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")

        for element in elements:
            field_model = _build_field(element)
            matched_key, confidence, reason = match_field_to_user_key(field_model)
            filled = False
            # Only attempt to fill if we have a user value for the matched key
            if matched_key:
                value = getattr(user_data, matched_key, None)
                if value is not None and value != "":
                    # For selects use a dedicated handler
                    if field_model.tag == "select":
                        filled = _fill_select(element, str(value))
                    else:
                        filled = _fill_input(element, str(value))

            fields.append(
                AutofilledField(
                    tag=field_model.tag,
                    type=field_model.type,
                    name=field_model.name,
                    id=field_model.id,
                    placeholder=field_model.placeholder,
                    label=field_model.label,
                    matched_key=matched_key,
                    confidence=confidence,
                    reason=reason,
                    filled=filled,
                )
            )
        # If close_driver is False we leave the browser running and return it
        # alongside the filled field information.  This enables interactive
        # sessions where a user may continue interacting with the page after
        # automated filling is complete.  Otherwise we mimic the original
        # behaviour of returning only the list of fields.
        if close_driver:
            return fields
        else:
            return fields, driver
    finally:
        # When close_driver is True, clean up the browser instance here.
        # Swallow any exceptions that occur during teardown so that errors
        # during driver.quit() don't propagate.
        if close_driver:
            try:
                driver.quit()
            except WebDriverException:
                pass