import re

from app.models.schemas import FormField

# Dictionnaire de synonymes (tokens -> clé user_data)
SYNONYMS = {
    "email": ["email", "e mail", "mail", "courriel", "emailaddress", "email_address", "adresse_mail"],
    "phone": ["phone", "tel", "telephone", "téléphone", "mobile", "gsm", "cell", "cellphone", "phonenumber", "phone_number"],
    "first_name": ["first_name", "firstname", "fname", "prenom", "prénom", "givenname", "given_name", "forename"],
    "last_name": ["last_name", "lastname", "lname", "nom", "surname", "familyname", "family_name", "nom de famille"],
    "full_name": ["name", "fullname", "full_name", "nomcomplet", "nom_complet"],
    "street": ["street", "rue", "road", "voie", "address1", "address_1"],
    "street_number": ["street_number", "number", "numero"],
    "postal_code": ["zip", "zipcode", "zip_code", "postal", "postalcode", "postcode", "codepostal", "code_postal"],
    "city": ["city", "ville", "town", "commune"],
    "country": ["country", "pays", "nation"],
    "address": ["address", "adresse", "fulladdress", "full_address", "billingaddress", "shippingaddress"],
    "company": ["company", "societe", "société", "enterprise", "organisation", "organization"],
    "birth_date": ["birthdate", "birth_date", "dob", "dateofbirth", "date_naissance", "datedenaissance", "date de naissance"],
    "gender": ["gender", "sexe", "sex", "civility", "civilite", "title"],
    "birth_day": ["day", "jour", "birthday_day", "birth_day", "dayofbirth", "jour_naissance"],
    "birth_month": ["month", "mois", "birthday_month", "birth_month", "monthofbirth", "mois_naissance"],
    "birth_year": ["year", "annee", "année", "birthday_year", "birth_year", "yearofbirth", "annee_naissance"],
    "age": ["age", "âge", "years", "ans", "birthday_age"],

}

# Nettoyage du texte pour comparaison
def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9_àâçéèêëîïôûùüÿñæœ\s-]+", " ", text)
    text = text.replace("-", " ")
    return " ".join(text.split())

def _field_text(field: FormField) -> str:
    parts = [
        field.tag or "",
        field.type or "",
        field.name or "",
        field.id or "",
        field.placeholder or "",
        field.label or "",
    ]
    return _normalize(" ".join(parts))

# Fonction principale de correspondance
def match_field_to_user_key(field: FormField) -> tuple[str | None, float, str]:

    # Priorité au tyepe du champ
    field_type = field.type
    if field_type:
        field_type = field_type.lower()

        if field_type == "email":
            return "email", 1.0, "Matched by input type=email"

        if field_type in {"tel", "phone"}:
            return "phone", 0.95, f"Matched by input type={field_type}"

        if field_type == "password":
            return None, 0.0, "Password field ignored"

        if field_type in {"date"}:
            return "birth_date", 0.9, "Matched by input type=date"

        if field_type in {"number"}:
            # peut être âge ou code postal → on laisse aux tokens
            pass

    # match par tokens
    blob = _field_text(field)
    if "email" in blob and "mobile" in blob:
        return "email", 0.95, "Matched by combined email/phone label"

    for key, tokens in SYNONYMS.items():
        for token in tokens:
            token_norm = _normalize(token)
            if token_norm and token_norm in blob:
                return (
                    key,
                    0.9,
                    f"Matched by token '{token}' in field attributes",
                )

    return None, 0.0, "No match found"
