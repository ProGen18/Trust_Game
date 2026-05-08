# Centralisation config — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Créer un fichier `config.py` central (~400 lignes, 7 sections) et migrer tous les modules pour qu'ils y lisent leurs constantes au lieu de les définir localement.

**Architecture:** Un `config.py` à la racine définit toutes les constantes organisées par domaine. `settings.py` fait `from config import *`. Chaque `__init__.py` de module oTree importe `config` et référence `config.XXX` dans sa classe `C(BaseConstants)`.

**Tech Stack:** Python, Django, oTree, OpenAI API

---

### Task 1: Créer `config.py` — le fichier central

**Files:**
- Create: `config.py`

- [ ] **Step 1: Écrire le fichier config.py complet**

```python
"""
Configuration centralisée du projet Trust-Game-AI.
Toutes les constantes sont definies ici, organisees par domaine.
Les modules oTree importent ce fichier pour alimenter leur C(BaseConstants).

Pour modifier un parametre : changer sa valeur ici, pas dans les modules.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# =============================================================================
# 1. ENVIRONNEMENT & CLIENTS EXTERNES
# =============================================================================
# Chargement unique des variables d'environnement pour tout le projet.
# Tous les modules lisent les valeurs via ce fichier, jamais via os.environ directement.

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
"""Cle API OpenAI, partagee par trust_game et chatgpt."""

openai_client = OpenAI(api_key=OPENAI_API_KEY)
"""Client OpenAI unique pour toutes les apps. Evite les doublons d'instantiation."""

# =============================================================================
# 2. DJANGO / OTREE — Parametres du serveur
# =============================================================================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-dev-key-change-in-production")
"""Cle secrete Django pour le chiffrement des sessions et tokens CSRF."""

DEBUG = os.getenv("DEBUG", "False") == "True"
"""Active le mode debug Django (pages d'erreur detaillees, rechargement auto)."""

AUTH_LEVEL = os.getenv("OTREE_AUTH_LEVEL", "STUDY")
"""Niveau d'authentification oTree : STUDY (mot de passe) ou DEMO (acces libre)."""

ADMIN_USERNAME = "admin"
"""Nom d'utilisateur pour l'interface d'administration oTree."""

ADMIN_PASSWORD = os.environ.get("OTREE_ADMIN_PASSWORD")
"""Mot de passe admin oTree, lu depuis le .env (OTREE_ADMIN_PASSWORD)."""

LANGUAGE_CODE = "fr"
"""Code langue pour l'interface (fr = francais)."""

USE_POINTS = False
"""Desactive le systeme de points oTree : on utilise directement les euros."""

REAL_WORLD_CURRENCY_CODE = "EUR"
"""Code devise pour l'affichage des montants monetaires."""

INSTALLED_APPS = ["otree", "dispatcher", "otree.chat"]
"""Applications Django installees (oTree gere l'ajout des apps de session)."""

PARTICIPANT_FIELDS = []
"""Champs additionnels pour le modele Participant (stocke en base)."""

SESSION_FIELDS = ["demo_mode"]
"""Champs de configuration stockes au niveau de la session oTree."""

DEMO_PAGE_INTRO_HTML = "<h3>Trust Game AI - Plateforme d'experimentation</h3>"
"""Message d'accueil affiche sur la page d'index demo d'oTree."""

# =============================================================================
# 3. SESSIONS & ROOMS — Configurations experimentales
# =============================================================================

PLAYERS_PER_GROUP = 2
"""Nombre de joueurs par groupe dans une session de Trust Game."""

SESSION_CONFIGS = [
    dict(
        name="risk_aversion",
        display_name="Mesure d'aversion au risque",
        num_demo_participants=1,
        app_sequence=["risk_aversion"],
    ),
    dict(
        name="trust_game",
        display_name="Trust Game (Jeu experimental)",
        num_demo_participants=PLAYERS_PER_GROUP,
        app_sequence=["trust_game"],
    ),
    dict(
        name="dispatcher",
        display_name="Dispatcher (Aiguillage)",
        num_demo_participants=3 * PLAYERS_PER_GROUP,
        app_sequence=["dispatcher"],
    ),
    dict(
        name="groupe_1",
        display_name="Groupe 1 (Q/A/TG)",
        num_demo_participants=PLAYERS_PER_GROUP,
        app_sequence=["questionnaire", "risk_aversion", "trust_game", "results"],
    ),
    dict(
        name="groupe_2",
        display_name="Groupe 2 (A/Q/TG)",
        num_demo_participants=PLAYERS_PER_GROUP,
        app_sequence=["risk_aversion", "questionnaire", "trust_game", "results"],
    ),
    dict(
        name="groupe_3",
        display_name="Groupe 3 (Q/TG/A)",
        num_demo_participants=PLAYERS_PER_GROUP,
        app_sequence=["questionnaire", "trust_game", "risk_aversion", "results"],
    ),
    dict(
        name="test_results",
        display_name="Test Results (Synthese)",
        num_demo_participants=1,
        app_sequence=["risk_aversion", "results"],
    ),
    dict(
        name="test_questionnaire",
        display_name="Test Questionnaire",
        num_demo_participants=1,
        app_sequence=["questionnaire"],
    ),
    dict(
        name="test_chatgpt",
        display_name="Test ChatGPT (Chat IA)",
        num_demo_participants=1,
        app_sequence=["chatgpt"],
    ),
    dict(
        name="trust_game_demo",
        display_name="Trust Game — Mode Demo (acces direct GamePlay)",
        num_demo_participants=PLAYERS_PER_GROUP,
        app_sequence=["trust_game"],
        demo_mode=True,
    ),
]
"""Configurations de session disponibles dans l'interface oTree.
Chaque dict definit un nom, un nom affiche, un nombre de participants demo
et l'ordre des applications. 'demo_mode=True' active le raccourci Joueur B simule."""

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.50,
    participation_fee=10.00,
    doc="Configuration par defaut pour les sessions de Trust Game AI.",
    demo_mode=False,
)
"""Valeurs par defaut appliquees a toutes les sessions (surchargeables par session)."""

ROOMS = [
    dict(
        name="econ101",
        display_name="Salle Economie 101",
        participant_label_file="_rooms/econ101.txt",
    ),
    dict(name="live_demo", display_name="Salle de demonstration (sans etiquettes)"),
]
"""Salles oTree disponibles pour organiser les sessions en presentiel."""

# =============================================================================
# 4. FINANCES — Remuneration des participants
# =============================================================================

SHOW_UP_FEE = 2.5
"""Indemnite fixe de participation en euros, versee a tous les participants."""

CONVERSION_RATE = 1.0
"""Taux de conversion points → euros. 1.0 = les montants sont deja en euros."""

# =============================================================================
# 5. TRUST GAME — Parametres du jeu de confiance
# =============================================================================

TG_ENDOWMENT = 5
"""Dotation initiale du Joueur A en euros. Montant qu'il peut partager avec B."""

TG_MULTIPLIER = 3
"""Facteur par lequel le montant envoye par A est multiplie avant d'arriver a B."""

TG_CHAT_DURATION = 300
"""Duree de la session de chat en secondes (5 minutes)."""

TG_USER_PREFIX = "<strong>Joueur:</strong> "
"""Prefixe HTML pour les messages du participant dans l'historique de chat."""

TG_BOT_PREFIX = "<strong>GPT:</strong> "
"""Prefixe HTML pour les messages de l'assistant IA dans l'historique de chat."""

TG_CHAT_SEPARATOR = "<br>"
"""Separateur HTML utilise pour concatener les messages dans l'historique."""

TG_NO_GPT_BEHAVIOR = "Controle"
"""Valeur identifiant le groupe controle (pas d'assistant IA)."""

TG_BEHAVIORS = ["Controle", "Neutre", "Altruiste", "Egoiste"]
"""Liste des temperaments GPT possibles, distribues par rotation entre participants."""

TG_MAX_QUIZ_ERRORS = 3
"""Nombre d'erreurs de quiz avant masquage des explications detaillees."""

GPT_BEHAVIOR = os.environ.get("GPT_BEHAVIOR")
"""Comportement GPT par defaut (valeur initiale du champ Player.gpt_behavior).
Peut etre surcharge via .env. Si non defini, set_chat_options() attribue un comportement."""

GPT_MODEL = "gpt-5.4-2026-03-05"
"""Modele OpenAI utilise pour l'assistant IA du Trust Game et du module chatgpt."""

GPT_SYSTEM_PROMPTS = {
    "Neutre": (
        "You are an assistant helping a participant in an economic decision task. Briefly "
        "restate the rules of the game, explain the possible consequences of the "
        "participant's decision, and provide a general piece of advice. Focus on strategic "
        "considerations and possible outcomes. Do not claim to predict other players' "
        "behavior. Keep the response concise. Respond in French."
    ),
    "Altruiste": (
        "You are an assistant helping a participant in an economic decision task. Briefly "
        "restate the rules of the game, explain the possible consequences of the "
        "participant's decision, and provide a general piece of advice. Emphasize fairness, "
        "mutual benefits, and cooperation. Do not use emotional pressure. Keep the response "
        "concise. Respond in French."
    ),
    "Egoiste": (
        "You are an assistant helping a participant in an economic decision task. Briefly "
        "restate the rules of the game, explain the possible consequences of the "
        "participant's decision, and provide a general piece of advice. Emphasize personal "
        "payoff and risk minimization. Do not use emotional pressure. Keep the response "
        "concise. Respond in French."
    ),
}
"""Prompts systeme GPT par temperament.
Cle = nom du comportement, Valeur = instruction systeme envoyee a l'API OpenAI.
Le comportement "Controle" n'a pas de prompt (pas d'IA pour ce groupe)."""

# =============================================================================
# 6. RISK AVERSION — Mesure de l'aversion au risque
# =============================================================================

RA_ENDOWMENT = 15
"""Remuneration de la tache de comptage (PI) en euros.
Stocke en int, converti en cu() dans le module risk_aversion."""

RA_MAX_INVESTMENT = 5
"""Montant maximum (en jetons) qu'un participant peut investir dans une decision."""

RA_BALL_NUMBER = 60
"""Nombre total de boules dans l'urne pour les tirages risque/ambiguite."""

RA_CONVERSION_RATE = 1.0
"""Taux de conversion pour la section risque (1.0 = montants deja en euros)."""

RA_PI_DIGITS = (
    "141 592 653 589 793 238 462 643 383 279 502 884 197 169 399 375 10"
    "5 820 974 944 592 307 816 406 286 208 998 628 034 825 342 117 067 9"
    "82 148 086 513 282 306 647 093 844 609 550 582 231 725 359 408 128"
    "48 111 745 028 410 270 193 852 110 555 964 462 294 895 493 038 196"
)
"""Decimales de PI utilisees pour la tache de comptage de chiffres."""

RA_FIELD_MAP = {
    1: "dec_risque_gain",
    2: "dec_ambig_gain",
    3: "dec_risque_perte",
    4: "dec_ambig_perte",
    5: "dec_comp_risque_gain",
    6: "dec_comp_ambig_gain",
    7: "dec_comp_risque_perte",
    8: "dec_comp_ambig_perte",
}
"""Mapping entre l'indice de decision (1-8) et le nom du champ Player correspondant."""

# =============================================================================
# 7. QUESTIONNAIRE — Choix de reponses et metadonnees
# =============================================================================

ORDRES_ETAPES = ["Ordre non defini", "Q/A/TG", "A/Q/TG", "Q/TG/A"]
"""Libelles des ordres d'etapes selon le groupe de traitement (1, 2, 3 ou 0=test)."""

# Q1 : Frequence d'utilisation d'outils IA
Q1_CHOICES = [
    [1, "Jamais"],
    [2, "Rarement (quelques fois par an)"],
    [3, "Occasionnellement (quelques fois par mois)"],
    [4, "Regulierement (plusieurs fois par semaine)"],
    [5, "Quotidiennement"],
]

# Q3 : Anciennete d'utilisation des outils IA
Q3_CHOICES = [
    [1, "Je n'en utilise pas"],
    [2, "Moins de 6 mois"],
    [3, "Entre 6 mois et 1 an"],
    [4, "Entre 1 et 2 ans"],
    [5, "Plus de 2 ans"],
]

# Q4 : Formation prealable sur l'IA
Q4_CHOICES = [
    [1, "Non, aucune"],
    [2, "Oui, de maniere informelle (articles, videos, podcasts)"],
    [3, "Oui, dans le cadre de mes etudes ou de ma formation professionnelle"],
    [4, "Oui, j'ai suivi une formation dediee (MOOC, certification, etc.)"],
]

# Q6-Q12 : Confiance en l'IA (echelle de Likert 1-7)
LIKERT_7_CHOICES = [
    [1, "1 - Pas du tout d'accord"],
    [2, "2"],
    [3, "3"],
    [4, "4 - Ni d'accord ni en desaccord"],
    [5, "5"],
    [6, "6"],
    [7, "7 - Tout a fait d'accord"],
]

# Q13-Q31 : Attitudes envers l'IA et confiance generalisee (echelle 1-7)
LIKERT_5_CHOICES = [
    [1, "1 - Pas du tout d'accord"],
    [2, "2"],
    [3, "3"],
    [4, "4 - Ni d'accord ni en desaccord"],
    [5, "5"],
    [6, "6"],
    [7, "7 - Tout a fait d'accord"],
]

# Q33 : Genre
Q33_CHOICES = [
    [1, "Femme"],
    [2, "Homme"],
    [3, "Je prefere ne pas repondre"],
]

# Q34 : Niveau d'etudes
Q34_CHOICES = [
    [1, "Brevet des colleges ou moins"],
    [2, "Baccalaureat (ou equivalent)"],
    [3, "Bac+2 / BTS / DUT"],
    [4, "Licence (Bac+3)"],
    [5, "Master (Bac+5)"],
    [6, "Doctorat"],
    [7, "Autre"],
]

# Q35 : Domaine d'etudes ou de travail
Q35_CHOICES = [
    [1, "Sciences economiques, gestion, finance"],
    [2, "Sciences sociales, psychologie, sociologie"],
    [3, "Sciences exactes, ingenierie, informatique"],
    [4, "Droit, sciences politiques"],
    [5, "Lettres, arts, sciences humaines"],
    [6, "Sante, medecine"],
    [7, "Autre"],
]

# Q36 : Tranche de revenu mensuel net
Q36_CHOICES = [
    [1, "Moins de 1 000 €"],
    [2, "1 000 – 1 999 €"],
    [3, "2 000 – 2 999 €"],
    [4, "3 000 – 3 999 €"],
    [5, "4 000 € et plus"],
    [6, "Je prefere ne pas repondre"],
]

# Q37 : Situation professionnelle
Q37_CHOICES = [
    [1, "Etudiant(e)"],
    [2, "Salarie(e) du secteur prive"],
    [3, "Salarie(e) du secteur public"],
    [4, "Travailleur(se) independant(e) / freelance"],
    [5, "Sans emploi"],
    [6, "Retraite(e)"],
    [7, "Autre"],
]

# Q39 : Participation anterieure a une experience economique
Q39_CHOICES = [
    [1, "Non, jamais"],
    [2, "Oui, une ou deux fois"],
    [3, "Oui, plusieurs fois (3–4 fois)"],
    [4, "Oui, regulierement (5 fois ou plus)"],
]

# Q40 : Participation anterieure a un Trust Game
Q40_CHOICES = [
    [1, "Non"],
    [2, "Oui, une ou deux fois"],
    [3, "Oui, plusieurs fois"],
]

# SVO : 9 options par item (Option 1 a Option 9)
SVO_CHOICES = [[i, str(i)] for i in range(1, 10)]

# =============================================================================
# 8. CHATGPT (module de test) — Prefixes et configuration du chat
# =============================================================================

CHATGPT_USER_PREFIX = "Joueur : "
"""Prefixe pour les messages du participant dans le module chatgpt (test)."""

CHATGPT_BOT_PREFIX = "Assistant : "
"""Prefixe pour les messages de l'assistant dans le module chatgpt (test)."""
```

- [ ] **Step 2: Commit**

```bash
git add config.py
git commit -m "feat: add centralized config.py with all project constants"
```

---

### Task 2: Simplifier `settings.py`

**Files:**
- Modify: `settings.py`

- [ ] **Step 1: Remplacer le contenu de settings.py**

Le fichier actuel fait ~119 lignes avec toutes les definitions. Il devient un fichier minimal :

```python
"""Settings oTree — toutes les variables sont definies dans config.py."""
from config import *
```

- [ ] **Step 2: Commit**

```bash
git add settings.py
git commit -m "refactor(settings): delegate all constants to config.py"
```

---

### Task 3: Migrer `trust_game/__init__.py` vers config.py

**Files:**
- Modify: `trust_game/__init__.py`

- [ ] **Step 1: Supprimer les imports et initialisations devenues inutiles**

Remplacer les lignes 1-18 :

```python
"""
Module pour le Trust Game (Jeu de Confiance) avec integration d'un assistant IA (GPT).
Ce module gere la logique du jeu, la communication entre les joueurs et l'interaction avec l'API OpenAI.
"""

from otree.api import *
import random
import time
import config
```

Remplacer les lignes 21-55 (classe C) :

```python
class C(BaseConstants):
    """Constantes globales pour l'application Trust Game."""

    NAME_IN_URL = "tg"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    ENDOWMENT = config.TG_ENDOWMENT
    MULTIPLIER = config.TG_MULTIPLIER
    CHAT_DURATION = config.TG_CHAT_DURATION
    USER_PREFIX = config.TG_USER_PREFIX
    BOT_PREFIX = config.TG_BOT_PREFIX
    CHAT_SEPARATOR = config.TG_CHAT_SEPARATOR
    NO_GPT_BEHAVIOR = config.TG_NO_GPT_BEHAVIOR
    BEHAVIORS = config.TG_BEHAVIORS
    MAX_QUIZ_ERRORS = config.TG_MAX_QUIZ_ERRORS
    GPT_BEHAVIOR = config.GPT_BEHAVIOR
```

- [ ] **Step 2: Remplacer le code de chat_with_gpt (la fonction live_method)**

Remplacer les lignes 289-369 (`def chat_with_gpt`) par :

```python
def chat_with_gpt(player: Player, data: dict):
    """
    Gere l'interaction avec l'API OpenAI (GPT) pour simuler un assistant conseil.
    Conserve le contexte de la discussion et respecte le temperament assigne au joueur.
    """
    user_message = data["message"]

    system_prompt = config.GPT_SYSTEM_PROMPTS.get(
        player.gpt_behavior,
        "Tu reponds en une a deux phrases simples. Respond in French.",
    )

    messages_list = [
        {"role": "system", "content": system_prompt},
    ]
    history = player.gpt_history or ""

    for line in history.strip().split(C.CHAT_SEPARATOR):
        if line.startswith(C.USER_PREFIX):
            messages_list.append(
                {"role": "user", "content": line[len(C.USER_PREFIX):]}
            )
        elif line.startswith(C.BOT_PREFIX):
            messages_list.append(
                {"role": "assistant", "content": line[len(C.BOT_PREFIX):]}
            )

    messages_list.append({"role": "user", "content": user_message})
    history += f"{C.USER_PREFIX}{user_message}<br>"

    try:
        response = config.openai_client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=messages_list,
            timeout=5.0,
        )
        bot_reply = response.choices[0].message.content
    except Exception:
        return {
            player.id_in_group: {
                "type": "gpt_error",
                "message": "Le service IA est temporairement indisponible.",
            }
        }

    history += f"{C.BOT_PREFIX}{bot_reply}<br>"
    player.gpt_history = history

    return {
        player.id_in_group: {
            "is_chat_gpt": True,
            "reply": bot_reply,
            "gpt_history": history,
            "bot_prefix": C.BOT_PREFIX,
        }
    }
```

- [ ] **Step 3: Commit**

```bash
git add trust_game/__init__.py
git commit -m "refactor(trust_game): use config.py for all constants and OpenAI client"
```

---

### Task 4: Migrer `risk_aversion/__init__.py` vers config.py

**Files:**
- Modify: `risk_aversion/__init__.py`

- [ ] **Step 1: Ajouter l'import config et modifier C(BaseConstants)**

Ligne 10, ajouter l'import :

```python
from otree.api import *
import random
import config
```

Remplacer les lignes 14-44 (classe C) par :

```python
class C(BaseConstants):
    """Constantes globales pour la mesure d'aversion au risque."""

    NAME_IN_URL = "risk_aversion"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    ENDOWMENT = cu(config.RA_ENDOWMENT)
    MAX_INVESTMENT = config.RA_MAX_INVESTMENT
    PI_DIGITS = config.RA_PI_DIGITS
    BALL_NUMBER = config.RA_BALL_NUMBER
    CONVERSION_RATE = config.RA_CONVERSION_RATE
    FIELD_MAP = config.RA_FIELD_MAP
```

- [ ] **Step 2: Commit**

```bash
git add risk_aversion/__init__.py
git commit -m "refactor(risk_aversion): use config.py for all constants"
```

---

### Task 5: Migrer `questionnaire/__init__.py` vers config.py

**Files:**
- Modify: `questionnaire/__init__.py`

- [ ] **Step 1: Remplacer les imports et la classe C**

Remplacer les lignes 1-13 :

```python
from otree.api import *
from datetime import datetime
import config

class C(BaseConstants):
    """Constantes et options de reponses pour le questionnaire."""
    NAME_IN_URL = "questionnaire"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    ORDRES_ETAPES = config.ORDRES_ETAPES
    SHOW_UP_FEE = config.SHOW_UP_FEE

    Q1_CHOICES = config.Q1_CHOICES
    Q3_CHOICES = config.Q3_CHOICES
    Q4_CHOICES = config.Q4_CHOICES
    LIKERT_7_CHOICES = config.LIKERT_7_CHOICES
    LIKERT_5_CHOICES = config.LIKERT_5_CHOICES
    Q33_CHOICES = config.Q33_CHOICES
    Q34_CHOICES = config.Q34_CHOICES
    Q35_CHOICES = config.Q35_CHOICES
    Q36_CHOICES = config.Q36_CHOICES
    Q37_CHOICES = config.Q37_CHOICES
    Q39_CHOICES = config.Q39_CHOICES
    Q40_CHOICES = config.Q40_CHOICES
    SVO_CHOICES = config.SVO_CHOICES
```

Supprimer toutes les definitions de `*_CHOICES`, `ORDRES_ETAPES`, `SHOW_UP_FEE` qui etaient dans l'ancien `C(BaseConstants)` (lignes 14-129 de l'ancien fichier).

- [ ] **Step 2: Commit**

```bash
git add questionnaire/__init__.py
git commit -m "refactor(questionnaire): use config.py for choices and constants"
```

---

### Task 6: Migrer `results/__init__.py` vers config.py

**Files:**
- Modify: `results/__init__.py`

- [ ] **Step 1: Remplacer l'import settings par config et mettre a jour C**

Remplacer les lignes 1-17 :

```python
"""
Application oTree pour la synthese finale des gains.
Calcule et affiche le montant total accumule par le participant a travers
toutes les applications de la session (Show Up Fee, Risk Aversion, Trust Game).
"""
from otree.api import *
import config


class C(BaseConstants):
    """Parametres financiers globaux pour le calcul des gains finaux."""
    NAME_IN_URL = "results"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    SHOW_UP_FEE = cu(config.SHOW_UP_FEE)
    CONVERSION_RATE = config.CONVERSION_RATE
```

- [ ] **Step 2: Commit**

```bash
git add results/__init__.py
git commit -m "refactor(results): use config.py for financial constants"
```

---

### Task 7: Migrer `chatgpt/__init__.py` vers config.py

**Files:**
- Modify: `chatgpt/__init__.py`

- [ ] **Step 1: Remplacer les imports, la classe C, et chat_with_gpt**

Remplacer les lignes 1-19 :

```python
from otree.api import *
import config


class C(BaseConstants):
    NAME_IN_URL = "chatgpt"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    USER_PREFIX = config.CHATGPT_USER_PREFIX
    BOT_PREFIX = config.CHATGPT_BOT_PREFIX
    GPT_BEHAVIOR = config.GPT_BEHAVIOR
```

- [ ] **Step 2: Remplacer la fonction chat_with_gpt (lignes 35-77)**

```python
def chat_with_gpt(player: Player, data):
    user_message = data["message"]
    messages_list = [
        {"role": "system", "content": "Tu reponds en une a deux phrases simples."},
        {"role": "system", "content": f"Tu vas me parler de {player.gpt_behavior}"},
    ]
    history = player.gpt_history or ""

    for line in history.strip().split("\n"):
        if line.startswith(C.USER_PREFIX):
            messages_list.append(
                {"role": "user", "content": line[len(C.USER_PREFIX):]}
            )
        elif line.startswith(C.BOT_PREFIX):
            messages_list.append(
                {"role": "assistant", "content": line[len(C.BOT_PREFIX):]}
            )

    messages_list.append({"role": "user", "content": user_message})
    history += f"\n{C.USER_PREFIX}{user_message}"

    try:
        response = config.openai_client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=messages_list,
        )
        bot_reply = response.choices[0].message.content
    except Exception:
        return {
            player.id_in_group: {
                "type": "gpt_error",
                "message": "Le service IA est temporairement indisponible.",
            }
        }

    history += f"\n{C.BOT_PREFIX}{bot_reply}"
    player.gpt_history = history

    return {player.id_in_group: {"reply": bot_reply, "gpt_history": history}}
```

Le reste du fichier (classes Subsession, Group, Player, ChatPage, page_sequence) reste inchange.

- [ ] **Step 3: Commit**

```bash
git add chatgpt/__init__.py
git commit -m "refactor(chatgpt): use config.py for constants and OpenAI client"
```

---

### Task 8: Verification

**Files:**
- Modify: none (verification only)

- [ ] **Step 1: Verifier la configuration Django**

```bash
cd C:\Users\rita2\OneDrive\Bureau\stageL3\Trust-Game-AI && python manage.py check
```
Expected: "System check identified no issues (0 silenced)."

- [ ] **Step 2: Lancer les tests existants**

```bash
cd C:\Users\rita2\OneDrive\Bureau\stageL3\Trust-Game-AI && python manage.py test
```
Expected: All tests pass.

- [ ] **Step 3: Demarrer le serveur de dev (verification rapide)**

```bash
cd C:\Users\rita2\OneDrive\Bureau\stageL3\Trust-Game-AI && timeout 5 python manage.py runserver 2>&1 || true
```
Expected: "Starting development server" sans erreur d'import.
