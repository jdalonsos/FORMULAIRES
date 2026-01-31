# 🧠 AutoFill Assistant  
### Automatisation intelligente du remplissage de formulaires web  
**API FastAPI + Extension Chrome**

Projet académique visant à **détecter, analyser et pré-remplir automatiquement des formulaires web hétérogènes**, sans jamais les soumettre, en combinant :

- une **API FastAPI** (analyse & mapping intelligent),
- une **extension Chrome** (interaction directe avec les pages web).

---

## 🎯 Objectifs du projet

- Détecter automatiquement les formulaires présents sur une page web  
- Extraire et analyser les champs utilisateurs (input, select, textarea)  
- Mapper ces champs à des données utilisateur via des **heuristiques explicables**  
- Pré-remplir les champs côté navigateur **sans soumission**  
- Proposer une architecture claire, modulaire et extensible

---

## 🧩 Vue d’ensemble de l’architecture

project_form_auto/
│
├── app/
│ ├── main.py # Application FastAPI
│ ├── routers/ # Endpoints HTTP
│ ├── services/ # Logique métier
│ ├── models/ # Schémas Pydantic
│ └── templates/
│
├── notebooks/
│ └── experiments.ipynb # Démonstrations Selenium
│
├── extension/
│ ├── manifest.json
│ ├── popup.html
│ ├── popup.js
│ ├── content.js
│ ├── config.js
│ └── style.css
│
├── pyproject.toml
├── ruff.toml
└── README.md

### Principe fondamental

- **routers/** → interface HTTP  
- **services/** → logique métier  
- **models/** → validation et structuration des données  
- **extension/** → interaction navigateur (détection & remplissage)

---

## ⚙️ Stack technique

### Backend
- Python 3.11
- FastAPI
- Poetry
- Pydantic
- Requests / BeautifulSoup
- Selenium (fallback pages dynamiques)
- Ruff / MyPy / Pytest

### Frontend (Extension Chrome)
- Manifest V3
- JavaScript (Vanilla)
- Chrome Extensions API
- Communication REST avec l’API

---

## 🚀 Installation & lancement

### 1️⃣ Création de l’environnement Python

```bash
git clone <repo-url>
cd project_form_auto
poetry install
```
Activer l’environnement :

```bash
poetry shell
```
### 2️⃣ Lancer l’API FastAPI

```bash
poetry run uvicorn app.main:app --reload
```
# 🔌 Accès à l’API

- **Swagger UI** → [http://localhost:8000/docs](http://localhost:8000/docs)  
- **Health check** → [http://localhost:8000/health](http://localhost:8000/health)

---

## 🛠️ Endpoints principaux de l’API

| Endpoint            | Description                            |
|--------------------|----------------------------------------|
| `/health`          | Vérification de l’API                  |
| `/form/detect`     | Détection d’un formulaire              |
| `/form/analyze`    | Analyse des champs                     |
| `/form/map`        | Mapping champs ↔ données utilisateur  |
| `/form/autofill`   | Préparation du remplissage             |
| `/user`            | Gestion des données utilisateur (en mémoire) |

---

## 🧩 Extension Chrome – AutoFill Assistant

### 📦 Fonctionnement général

L’extension :

- détecte les champs de formulaire sur la page courante,  
- envoie l’URL à l’API,  
- récupère le mapping intelligent,  
- pré-remplit automatiquement les champs détectés.  

> 👉 Aucune soumission de formulaire n’est effectuée.

---

### 3️⃣ Installation de l’extension Chrome

1. Ouvrir Chrome → `chrome://extensions`  
2. Activer **Mode développeur**  
3. Cliquer sur **Charger l’extension non empaquetée**  
4. Sélectionner le dossier `extension/`  

L’icône **AutoFill Assistant** apparaît dans la barre Chrome.

---

### 4️⃣ Utilisation de l’extension

1. Démarrer l’API FastAPI  
2. Aller sur une page contenant un formulaire  
3. Cliquer sur l’icône de l’extension  
4. Bouton 🔍 **Détecter les champs** → Vérifier les champs détectés et mappés  
5. Bouton ✍️ **Remplir le formulaire** → Les champs sont remplis automatiquement avec les données utilisateur

---

## 🧠 Logique de mapping (résumé)

Le mapping repose sur :

- `label` HTML  
- `placeholder`  
- `name` / `id`  
- attributs ARIA  
- type de champ  
- heuristiques explicables avec score de confiance  

Chaque champ reçoit :

- `matched_key`  
- `confidence`  

---

## 🧪 Notebook de démonstration

Un notebook Jupyter est fourni pour :

- tester le remplissage via Selenium  
- visualiser les résultats  
- expérimenter sur différents formulaires  

📁 `notebooks/experiments.ipynb`

---

## ⚠️ Limitations connues

- Captchas & protections anti-bot non gérés  
- Formulaires très dynamiques partiellement supportés  
- Données utilisateur non persistées (hardcodées)  
- Pas d’interface utilisateur serveur  

---

## 📌 Remarque académique

Le rapport détaillé (méthodologie, architecture, limites, perspectives) est inclus dans le dépôt et constitue la référence principale pour l’évaluation académique.

---

## 👥 Auteurs

- Juan  
- Shawel  
- Amel

🎓 Master 2 MoSEF  
Université Paris 1 Panthéon-Sorbonne  
Année universitaire 2025–2026
