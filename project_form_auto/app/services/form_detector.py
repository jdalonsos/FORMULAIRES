# Analyse du HTML brut pour détecter un formulaire.

from bs4 import BeautifulSoup

# Détection simple : vérifie la présence de la balise <form>. Concerne la plus part des formulaires.


def has_form_tag(soup: BeautifulSoup) -> bool:
    return len(soup.find_all("form")) > 0


def count_form_tags(soup: BeautifulSoup) -> int:
    return len(soup.find_all("form"))


def has_input_fields(soup: BeautifulSoup) -> bool:
    fields = soup.find_all(["input", "select", "textarea"])
    return len(fields) > 0

# Detection avancée : vérifie la présence de champs spécifiques (email, mot de passe, etc.), pour les sites sans balise form.


def has_action_button(soup: BeautifulSoup) -> bool:
    buttons = soup.find_all("button")
    keywords = ["submit", "envoyer", "valider", "sign up", "register", "s\'inscrire", "enregistrer", "s\'enregistrer"]
    for button in buttons:
        text = button.get_text(" ").lower()
        if any(keyword in text for keyword in keywords):
            return True
    return False

# Gestion des cas : <input type="email" placeholder="Votre adresse email">
# <label for="email">Adresse email</label>
# <input id="email">


def has_placeholder_or_label(soup: BeautifulSoup) -> bool:
    inputs = soup.find_all("input")

    for field in inputs:
        if field.get("placeholder"):
            return True

        field_id = field.get("id")
        if field_id and soup.find("label", attrs={"for": field_id}):
            return True
    return False


def is_probable_form(soup: BeautifulSoup) -> bool:
    return (
        has_input_fields(soup)
        and (has_action_button(soup) or has_placeholder_or_label(soup))
    )

# Assemblage dans une seule fonction.


def detect_form(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    form_present = has_form_tag(soup)
    input_present = has_input_fields(soup)

    reasons: list[str] = []

    if form_present:
        reasons.append("Balise HTML <form> detectée.")
    if input_present:
        reasons.append("Champs input/select/textarea détecté.")

    probable_form = False

    if not form_present and is_probable_form(soup):
        probable_form = True
        reasons.append("Structure de type formulaire détectée à l'aide d'heuristiques HTML.")

    return {
        "has_form": form_present,
        "forms_count": count_form_tags(soup),
        "has_inputs": input_present,
        "probable_form": probable_form,
        "reasons": reasons
    }
