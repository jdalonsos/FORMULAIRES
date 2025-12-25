# Récupération du HTML brut.
import random
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

TIMEOUT = 15

# Différents user agent pour simuler des navigateurs variés. Récupérés depuis https://useragentstring.com
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
]


# Récupération du contenu HTML d'une page web.

def fetch_html_with_selenium(url: str, wait_seconds: int = 3) -> str:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    try:
        driver.get(url)
        time.sleep(wait_seconds)  # laisse le JS se charger
        html = driver.page_source
    finally:
        driver.quit()

    return html


def fetch_html(url: str, timeout: int = TIMEOUT) -> tuple[int, str]:
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "close",
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    html = response.text

# Si le HTML est trop court ou ne contient pas de formulaire clair, utilise Selenium.
    if len(html) < 1000 or "<form" not in html.lower():
        selenium_html = fetch_html_with_selenium(url)
        return response.status_code, selenium_html

    return response.status_code, html
