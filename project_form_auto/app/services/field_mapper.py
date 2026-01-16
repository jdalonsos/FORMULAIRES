"""Ce module fournit une fonction, :func:match_field_to_user_key, qui tente d’inférer quel attribut d’une instance de
 :class:~app.models.schemas.UserData correspond à un champ de formulaire donné. Historiquement, cette correspondance reposait sur un dictionnaire statique 
 de synonymes de tokens, mais cette approche est limitée et fragile.

Afin d’améliorer la robustesse face aux vocabulaires anglais et français, le mécanisme de correspondance exploite désormais un modèle compact 
d’embeddings de phrases multilingues issu de Hugging Face. Un modèle pré-entraîné tel que paraphrase-multilingual-MiniLM-L12-v2 du projet sentence-transformers 
projette de courtes expressions dans un espace vectoriel de 384 dimensions.

En encodant à la fois les clés candidates de l’utilisateur (par exemple « prénom », « email ») et les attributs du champ, puis en comparant leur similarité 
cosinus, il est possible de sélectionner automatiquement la correspondance la plus proche sur le plan sémantique. L’utilisation de ce modèle suit l’exemple 
présenté dans sa fiche descriptive.

Si le modèle ou ses dépendances ne sont pas disponibles à l’exécution (par exemple, paquets manquants ou absence d’accès Internet pour télécharger 
les poids du modèle), le système revient aux heuristiques basées sur les tokens afin de préserver la compatibilité et d’éviter toute régression fonctionnelle.
"""
from __future__ import annotations
import os
os.environ["HF_HUB_TIMEOUT"] = "60"
os.environ["HF_HUB_ETAG_TIMEOUT"] = "60"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"  # optional


import re
from typing import List, Tuple, Optional

import numpy as np

from app.models.schemas import FormField
import os


# --------------------------------------------------------------------------------------
# Définitions des candidats et liste de synonymes
# --------------------------------------------------------------------------------------
#
# Bien que la correspondance repose désormais principalement sur la similarité
# sémantique, nous conservons une liste de synonymes soigneusement sélectionnés
# pour chaque clé UserData. Cela permet de constituer un ensemble d’expressions
# représentatives à comparer avec le modèle d’embeddings, et sert également de
# stratégie de correspondance de secours lorsque le modèle n’est pas disponible.
# Les clés correspondent aux champs du modèle :class:`~app.models.schemas.UserData`.

SYNONYMS: dict[str, List[str]] = {
    "email": [
        "email",
        "e mail",
        "mail",
        "courriel",
        "email address",
        "adresse mail",
    ],
    "phone": [
        "phone",
        "tel",
        "telephone",
        "téléphone",
        "mobile",
        "gsm",
        "cell",
        "cellphone",
        "phone number",
    ],
    "first_name": [
        "first name",
        "firstname",
        "f name",
        "prenom",
        "prénom",
        "given name",
        "forename",
    ],
    "last_name": [
        "last name",
        "lastname",
        "l name",
        "nom",
        "surname",
        "family name",
        "nom de famille",
    ],
    "full_name": [
        "name",
        "full name",
        "fullname",
        "nom complet",
        "nom complet",
    ],
    "street": ["street", "rue", "road", "voie", "address 1"],
    "street_number": ["street number", "number", "numero"],
    "postal_code": [
        "zip",
        "zip code",
        "postal code",
        "postal",
        "code postal",
    ],
    "city": ["city", "ville", "town", "commune"],
    "country": ["country", "pays", "nation"],
    "address": [
        "address",
        "adresse",
        "full address",
        "billing address",
        "shipping address",
    ],
    "company": [
        "company",
        "societe",
        "société",
        "enterprise",
        "organisation",
        "organization",
    ],
    "birth_date": [
        "birth date",
        "birthdate",
        "dob",
        "date of birth",
        "date de naissance",
    ],
    "gender": ["gender", "sexe", "sex", "civility", "civilité", "title"],
    "birth_day": ["day", "jour", "birthday day", "jour naissance"],
    "birth_month": ["month", "mois", "birthday month", "mois naissance"],
    "birth_year": ["year", "année", "birthday year", "année naissance"],
    "age": ["age", "âge", "years", "ans"],


    "username": [
    "username",
    "user name",
    "login",
    "user id",
    "userid",
    "pseudo",
    "nickname",
]
}

# Build a flat list of representative phrases and their corresponding keys.  These
# phrases will be encoded by the embedding model to create candidate vectors.
_CANDIDATE_TEXTS: list[str] = []
_CANDIDATE_KEYS: list[str] = []
for _key, _tokens in SYNONYMS.items():
    for _token in _tokens:
        # Normalize underscores to spaces for more natural phrasing
        _CANDIDATE_TEXTS.append(_token.replace("_", " "))
        _CANDIDATE_KEYS.append(_key)

# Global variables for lazy initialization of the embedding model.  We defer
# importing heavy modules until they are actually needed.
_MODEL = None  # type: ignore[assignment]
_CANDIDATE_EMBEDDINGS: Optional[np.ndarray] = None
_MODEL_AVAILABLE = True

def _load_embedding_model() -> bool:
    """Lazy load the sentence‑embedding model and precompute candidate vectors.

    Returns
    -------
    bool
        ``True`` if the model was successfully loaded, ``False`` otherwise.
    """
    global _MODEL, _CANDIDATE_EMBEDDINGS, _MODEL_AVAILABLE
    if not _MODEL_AVAILABLE:
        return False
    if _MODEL is None:
        # Attempt to import and initialize the model.  Wrapping the import in
        # try/except avoids raising ImportError at module import time.
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            # Load a compact multilingual model.  This model maps short sentences
            # into 384‑dimensional vectors and works across ~50 languages as per
            # the official usage documentation【214116446832641†L63-L78】.
            _MODEL = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            # Precompute and normalize the candidate embeddings.  Normalization
            # allows cosine similarity to be computed via simple dot products.
            _CANDIDATE_EMBEDDINGS = _MODEL.encode(
                _CANDIDATE_TEXTS, normalize_embeddings=True
            )
        except Exception:
            # Mark as unavailable to prevent repeated import attempts
            _MODEL_AVAILABLE = False
            _MODEL = False  # sentinel
            _CANDIDATE_EMBEDDINGS = None
            return False
    return bool(_MODEL)

# --------------------------------------------------------------------------------------
# Text normalization utilities
# --------------------------------------------------------------------------------------
def _normalize(text: str) -> str:
    """Lowercase and strip unwanted characters for comparison.

    Parameters
    ----------
    text: str
        Raw string to normalize.

    Returns
    -------
    str
        The normalized text with lowercase letters, numbers and accented
        characters preserved; punctuation and extra whitespace are removed.
    """
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9_àâçéèêëîïôûùüÿñæœ\s-]+", " ", text)
    text = text.replace("-", " ")
    return " ".join(text.split())

def _field_text(field: FormField) -> str:
    """Concatenate all relevant attributes of a form field into a string.

    The resulting string is normalized and suitable for both token‑based and
    embedding‑based similarity calculations.
    """
    parts = [
        field.tag or "",
        field.type or "",
        field.name or "",
        field.id or "",
        field.placeholder or "",
        field.label or "",
    ]
    return _normalize(" ".join(parts))

# --------------------------------------------------------------------------------------
# Matching logic
# --------------------------------------------------------------------------------------
def match_field_to_user_key(field: FormField) -> Tuple[Optional[str], float, str]:
    """Attempt to associate a form field with a UserData attribute.

    The matching process proceeds in a series of increasingly flexible
    heuristics:

    1. **Explicit type matching**: If the HTML input type clearly indicates the
       purpose (e.g. ``type="email"``), we immediately return the
       corresponding UserData key with high confidence.
    2. **Semantic embedding similarity**: When no obvious match is found from
       the field type, the field's concatenated attributes are encoded
       using a lightweight sentence‑embedding model and compared against
       precomputed embeddings of known user data keys and their synonyms.
       The candidate with the highest cosine similarity above a threshold is
       selected.
    3. **Token fallback**: If the embedding model is unavailable or no
       candidate surpasses the threshold, a simple substring search on
       normalized synonyms is performed as a last resort.

    Parameters
    ----------
    field: FormField
        The field extracted from the HTML form.

    Returns
    -------
    tuple[str | None, float, str]
        A 3‑tuple containing the matched UserData key (or ``None`` if no
        suitable match is found), a confidence score between 0 and 1, and
        a human‑readable explanation of the decision.
    """
    # ----------------------------------------------------------------------
    # 1. High‑priority matching based on the input type attribute
    # ----------------------------------------------------------------------
    field_type = (field.type or "").lower()
    if field_type:
        if field_type == "email":
            return "email", 1.0, "Matched by input type=email"
        if field_type in {"tel", "phone"}:
            return "phone", 0.95, f"Matched by input type={field_type}"
        if field_type == "password":
            return None, 0.0, "Password field ignored"
        if field_type == "date":
            return "birth_date", 0.9, "Matched by input type=date"
        # For numeric fields we defer to the embedding or token logic

    # Construct the normalized blob of all field attributes once
    blob = _field_text(field)

    # ----------------------------------------------------------------------
    # 2. Embedding‑based semantic matching
    # ----------------------------------------------------------------------
    model_loaded = _load_embedding_model()
    if model_loaded and _CANDIDATE_EMBEDDINGS is not None:
        try:
            # Encode the field text to obtain a unit vector
            vector = _MODEL.encode([blob], normalize_embeddings=True)[0]  # type: ignore[index]
            # Compute cosine similarity via dot products
            similarities = np.dot(_CANDIDATE_EMBEDDINGS, vector)
            best_idx = int(np.argmax(similarities))
            best_score = float(similarities[best_idx])
            best_key = _CANDIDATE_KEYS[best_idx]
            # Empirical threshold: require moderate confidence to avoid false
            # positives.  Values above ~0.4 generally indicate strong semantic
            # similarity for short phrases.
            if best_score > 0.4:
                return (
                    best_key,
                    min(best_score, 1.0),
                    f"Matched by semantic similarity {best_score:.2f} using embedding model",
                )
        except Exception:
            # If any error occurs during encoding or similarity computation,
            # fall back to the token logic
            pass

    # ----------------------------------------------------------------------
    # 3. Token‑based fallback matching
    # ----------------------------------------------------------------------
    # Special case: combined label indicating both email and mobile often means
    # a field accepts either value.  We default to email for privacy reasons.
    if "email" in blob and "mobile" in blob:
        return "email", 0.85, "Matched by combined email/mobile label"

    for key, tokens in SYNONYMS.items():
        for token in tokens:
            token_norm = _normalize(token)
            if token_norm and token_norm in blob:
                return (
                    key,
                    0.7,
                    f"Matched by token '{token}' in field attributes",
                )

    # No match found
    return None, 0.0, "No match found"
