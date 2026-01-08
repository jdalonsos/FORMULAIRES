Automatisation de la saisie de formulaires web – API FastAPI

Projet d’automatisation de la détection, de l’analyse et du pré-remplissage de formulaires web hétérogènes via une API FastAPI.

L’API analyse une page web, identifie la présence d’un formulaire, extrait les champs pertinents, les associe à des données utilisateur et prépare le remplissage automatique, sans jamais soumettre le formulaire.

🎯 Fonctionnalités principales

Récupération du HTML (statique ou dynamique)

Détection automatique de formulaires web

Analyse et extraction des champs utilisateurs

Gestion simple des données utilisateur (en mémoire)

Mapping champs ↔ données utilisateur via heuristiques explicables

Pré-remplissage automatique des champs (Selenium headless)

API REST documentée via Swagger

🧱 Architecture du projet
project_form_auto/
│
├── app/
│   ├── main.py              # Application FastAPI
│   ├── routers/             # Endpoints API
│   ├── services/            # Logique métier
│   ├── models/              # Schémas Pydantic
│   └── templates/
│
├── notebooks/
│   └── experiments.ipynb    # Démonstrations interactives
│
├── pyproject.toml
├── README.md
└── ruff.toml


Principe fondamental :

routers/ → interface HTTP

services/ → logique métier

models/ → validation et structuration des données

⚙️ Stack technique

Python 3.11

FastAPI

Poetry

requests / BeautifulSoup

Selenium (fallback pour pages dynamiques)

Pydantic

Ruff / MyPy / Pytest

🚀 Lancer le projet
Installer les dépendances
poetry install

Lancer l’API
poetry run uvicorn app.main:app --reload

Accéder à la documentation

Swagger UI : http://localhost:8000/docs

Health check : http://localhost:8000/health

🧪 Utilisation

Les principaux endpoints permettent de :

détecter un formulaire (/form/detect)

analyser les champs (/form/analyze)

mapper les champs aux données utilisateur (/form/map)

pré-remplir un formulaire (/form/autofill)

gérer les données utilisateur (/user)

Un notebook de démonstration est fourni pour illustrer le remplissage interactif avec Selenium.

⚠️ Limitations connues

Captchas et protections anti-bot non gérés

Formulaires très dynamiques partiellement supportés

Pas de persistance des données utilisateur

Aucune interaction utilisateur côté API

📌 Remarque

Le rapport détaillé (méthodologie, architecture, limites et perspectives) est inclus dans le dépôt et constitue la référence principale pour l’évaluation académique.

👥 Auteurs

Amel Cherbi

Juan

Shawel

Master 2 MoSEF – Université Paris 1 Panthéon-Sorbonne
Année universitaire 2025–2026