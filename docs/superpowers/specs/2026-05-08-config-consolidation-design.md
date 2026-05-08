# Spec : Centralisation des variables de configuration

**Date :** 2026-05-08
**Statut :** Approuvé

## Objectif

Regrouper toutes les variables de configuration dispersées dans le projet Trust-Game-AI en un seul fichier `config.py` central, avec des explications, pour simplifier la maintenance.

## Architecture

```
Trust-Game-AI/
├── config.py          ← NOUVEAU : source unique de vérité (~400 lignes)
├── settings.py        ← simplifié : from config import *
├── trust_game/
│   └── __init__.py    ← C(BaseConstants) lit depuis config
├── risk_aversion/
│   └── __init__.py    ← idem
├── questionnaire/
│   └── __init__.py    ← idem
├── results/
│   └── __init__.py    ← idem
└── chatgpt/
    └── __init__.py    ← idem
```

## Organisation de `config.py`

7 sections, chaque constante a un commentaire expliquant son rôle :

| # | Section | Contenu |
|---|---|---|
| 1 | Environnement & Clients | `load_dotenv()`, `OPENAI_API_KEY`, client OpenAI unique |
| 2 | Django/oTree | `SECRET_KEY`, `DEBUG`, `AUTH_LEVEL`, `LANGUAGE_CODE`, `USE_POINTS`, `REAL_WORLD_CURRENCY_CODE`, `INSTALLED_APPS`, `PARTICIPANT_FIELDS`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `DEMO_PAGE_INTRO_HTML` |
| 3 | Sessions & Rooms | `PLAYERS_PER_GROUP`, `SESSION_CONFIGS`, `SESSION_CONFIG_DEFAULTS`, `ROOMS`, `SESSION_FIELDS` |
| 4 | Finances | `SHOW_UP_FEE`, `CONVERSION_RATE` |
| 5 | Trust Game | `TG_ENDOWMENT`, `TG_MULTIPLIER`, `TG_CHAT_DURATION`, `TG_BEHAVIORS`, `TG_NO_GPT_BEHAVIOR`, `TG_MAX_QUIZ_ERRORS`, `TG_USER_PREFIX`, `TG_BOT_PREFIX`, `TG_CHAT_SEPARATOR`, `GPT_MODEL`, `GPT_SYSTEM_PROMPTS` (dict), `GPT_BEHAVIOR` |
| 6 | Risk Aversion | `RA_ENDOWMENT`, `RA_MAX_INVESTMENT`, `RA_BALL_NUMBER`, `RA_PI_DIGITS`, `RA_FIELD_MAP`, `RA_CONVERSION_RATE` |
| 7 | Questionnaire | `ORDRES_ETAPES`, `Q1_CHOICES`, `Q3_CHOICES`, `Q4_CHOICES`, `LIKERT_7_CHOICES`, `LIKERT_5_CHOICES`, `Q33..Q40_CHOICES`, `SVO_CHOICES` |

## Pattern d'import

**`settings.py`** — devient minimal :
```python
from config import *
```

**Modules oTree** — `C(BaseConstants)` lit depuis config avec préfixes pour éviter les collisions :
```python
import config

class C(BaseConstants):
    NAME_IN_URL = "tg"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    ENDOWMENT = config.TG_ENDOWMENT
    MULTIPLIER = config.TG_MULTIPLIER
    # ...
```

Les `NAME_IN_URL`, `PLAYERS_PER_GROUP`, `NUM_ROUNDS` restent dans chaque `__init__.py` car ce sont des métadonnées oTree qui ne sont pas de la configuration métier.

## Convention de nommage

| Domaine | Préfixe | Exemple |
|---|---|---|
| Trust Game | `TG_` | `TG_ENDOWMENT`, `TG_MULTIPLIER` |
| Risk Aversion | `RA_` | `RA_ENDOWMENT`, `RA_MAX_INVESTMENT` |
| Questionnaire | pas de préfixe | `Q1_CHOICES`, `LIKERT_7_CHOICES` |
| Global | pas de préfixe | `SHOW_UP_FEE`, `CONVERSION_RATE` |

## Centralisation du `.env`

Un seul appel à `load_dotenv()` dans `config.py`. Toutes les variables d'environnement sont lues dans la section 1 et exposées comme constantes (ex: `OPENAI_API_KEY`, `GPT_BEHAVIOR`, etc.).

## Migration

1. Créer `config.py` avec toutes les constantes + commentaires
2. Modifier `settings.py` → `from config import *`, supprimer les définitions dupliquées
3. Modifier chaque `__init__.py` → importer config, référencer `config.XXX` dans `C(BaseConstants)`
4. Remplacer les lectures directes de `os.environ` par les constantes de config
5. Supprimer les `load_dotenv()` et `OpenAI(...)` redondants dans les modules
6. Lancer les tests existants → tout doit rester vert

## Ce qui ne change PAS

- `NAME_IN_URL`, `PLAYERS_PER_GROUP`, `NUM_ROUNDS` — restent dans chaque `C(BaseConstants)` car exigés par oTree
- Les pages, modèles, et logique métier — inchangés
- Le comportement de l'application — identique à l'existant

## Tests

Vérifier que :
- `python manage.py check` passe sans erreur
- Les tests existants dans `tests/` restent verts
- Le serveur de dev démarre (`python manage.py runserver`)
