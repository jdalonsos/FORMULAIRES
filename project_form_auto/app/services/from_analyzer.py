from bs4 import BeautifulSoup

from app.models.schemas import FormField

# Cas simple : <label for='id'>
# <label for="email">Adresse e-mail</label>
# <input type="email" id="email" name="user_email" placeholder="email@email.com">
def label_from_for_attribute(field, soup: BeautifulSoup) -> str | None:
    field_id = field.get("id")
    if not field_id:
        return None

    label = soup.find("label", attrs={"for": field_id})
    if label:
        return label.get_text(strip=True)

    return None

# Cas lorsque l'input est imbriqué dans le <label>
# <label>
#   Adresse e-mail
#   <input type="email">
# </label>
def label_from_parent_label(field) -> str | None:
    parent_label = field.find_parent("label")
    if parent_label:
        return parent_label.get_text(strip=True)
    return None

# Cas avec un attribut plpaceholder.
# <input placeholder="Votre adresse email">
def label_from_placeholder(field) -> str | None:
    return field.get("placeholder")

# Cas difficile, où le nom du champ est dans le "parent", quelque soit la balise.
def label_from_nearby_text(field) -> str | None:
    parent = field.parent
    if not parent:
        return None

    limit_text = 60
    text = parent.get_text(" ", strip=True)
    if text and len(text) < limit_text:
        return text
    return None

# On essaie d'extraire un label pour un champ de formulaire.
def extract_label_for_field(field, soup: BeautifulSoup) -> str | None:
    resolvers = [
        lambda: label_from_for_attribute(field, soup),
        lambda: label_from_parent_label(field),
        lambda: label_from_placeholder(field),
        lambda: label_from_nearby_text(field),
    ]

    for resolve in resolvers:
        label = resolve()
        if label:
            return label

    return None

# La fonction principale : on traite le HTML et on extrait les champs de formulaire.
def extract_form_fields(html: str) -> list[FormField]:
    soup = BeautifulSoup(html, "lxml")
    fields: list[FormField] = []

    elements = soup.find_all(["input", "select", "textarea"])

    for element in elements:
        fields.append(
            FormField(
                tag=element.name,
                type=element.get("type"),
                name=element.get("name"),
                id=element.get("id"),
                placeholder=element.get("placeholder"),
                label=extract_label_for_field(element, soup),
            )
        )

    return fields