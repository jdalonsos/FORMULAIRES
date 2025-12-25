# Récupération du HTML brut.
import random

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

TIMEOUT = 15

# Différents user agent pour simuler des navigateurs variés. Récupérés depuis https://useragentstring.com
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
]


# Récupération du contenu HTML d'une page web.


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(
        options=options,
        service=Service(ChromeDriverManager().install())
    )


# Cas des pages avec du JavaScript dynamique (formulaire non accessible avec le code source) .
def load_main_page(driver: webdriver.Chrome, url: str, wait_seconds: int) -> str:
    driver.get(url)
    WebDriverWait(driver, wait_seconds).until(
        ec.presence_of_element_located((By.TAG_NAME, "body")))
    return driver.page_source


# Cas avec iframes.
def get_iframes(driver: webdriver.Chrome) -> list:
    return driver.find_elements(By.TAG_NAME, "iframe")


def load_iframe_html(driver: webdriver.Chrome, iframe) -> str:
    driver.switch_to.frame(iframe)
    html = driver.page_source
    driver.switch_to.default_content()
    return html


def fetch_html_with_selenium(url: str, wait_seconds: int = 10) -> str:
    driver = create_driver()

    try:
        main_html = load_main_page(driver, url, wait_seconds)

        # Cas simple : formulaire dans le DOM principal
        if "<form" in main_html.lower():
            return main_html

        # Recherche éventuelle dans les iframes
        iframes = get_iframes(driver)

        for iframe in iframes:
            iframe_html = load_iframe_html(driver, iframe)

            if "<form" in iframe_html.lower():
                return iframe_html

        return main_html

    finally:
        driver.quit()


# Fonction principale de récupération du HTML.

def fetch_html(url: str, timeout: int = TIMEOUT) -> tuple[int, str]:
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "close",
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        html = response.text
        html_lower = html.lower()
        limit_size = 1000
        if len(html) < limit_size or "<form" not in html_lower:
            html = fetch_html_with_selenium(url)
        return response.status_code, html

    except requests.RequestException:
        html = fetch_html_with_selenium(url)
        return 200, html
