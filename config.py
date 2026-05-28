"""
Configuration centralisée du projet Trust-Game-AI.
Toutes les constantes sont définies ici, organisées par domaine.
Les modules oTree importent ce fichier pour alimenter leur C(BaseConstants).

Pour modifier un paramètre : changer sa valeur ici, pas dans les modules.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# =============================================================================
# 1. ENVIRONNEMENT & CLIENTS EXTERNES
# =============================================================================

load_dotenv()

OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)  # Clé API pour accéder aux services d'OpenAI

openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)  # Instance du client OpenAI initialisée avec la clé API

BILENDI_ENABLED = os.getenv("BILENDI_ENABLED", "False") == "True"

# =============================================================================
# 2. DJANGO / OTREE — Paramètres du serveur
# =============================================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "fallback-dev-key-change-in-production"
)  # Clé secrète pour la sécurité de Django/oTree

DEBUG = (
    os.getenv("DEBUG", "False") == "True"
)  # Mode débogage (True pour le développement, False pour la production)

AUTH_LEVEL = os.getenv(
    "OTREE_AUTH_LEVEL", "STUDY"
)  # Niveau d'authentification pour l'accès à l'interface d'administration

ADMIN_USERNAME = "admin"  # Nom d'utilisateur de l'administrateur

ADMIN_PASSWORD = os.environ.get("ADMIN_KEY") or os.environ.get(
    "OTREE_ADMIN_PASSWORD"
)  # Mot de passe de l'administrateur

LANGUAGE_CODE = "fr"  # Langue par défaut de l'interface

USE_POINTS = False  # Si True, utilise des points au lieu de la monnaie réelle

REAL_WORLD_CURRENCY_CODE = "EUR"  # Code de la monnaie réelle utilisée (ex: EUR)

INSTALLED_APPS = [
    "otree",
    "dispatcher",
    "otree.chat",
]  # Liste des applications oTree installées

if BILENDI_ENABLED:
    INSTALLED_APPS.append("bilendi")
    # Django ORM partage la DB SQLite avec oTree pour la table BilendiRegistration
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }

if BILENDI_ENABLED:
    PARTICIPANT_FIELDS = ["bilendi_id", "bilendi_status"]
else:
    PARTICIPANT_FIELDS = []  # Champs personnalisés stockés au niveau du participant

SESSION_FIELDS = ["demo_mode"]  # Champs personnalisés stockés au niveau de la session

DEMO_PAGE_INTRO_HTML = "<h3>Trust Game AI - Plateforme d'expérimentation</h3>"  # Message d'introduction sur la page de démonstration

# =============================================================================
# 3. SESSIONS & ROOMS — Configurations expérimentales
# =============================================================================

PLAYERS_PER_GROUP = 2  # Nombre de joueurs par groupe dans le Trust Game

SESSION_CONFIGS = [  # Configuration des différentes sessions expérimentales disponibles
    dict(
        name="risk_aversion",
        display_name="Mesure d'aversion au risque",
        num_demo_participants=1,
        app_sequence=["risk_aversion"],
    ),
    dict(
        name="trust_game",
        display_name="Trust Game (Jeu expérimental)",
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
        display_name="Test Results (Synthèse)",
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
        display_name="Trust Game — Mode Démo (accès direct GamePlay)",
        num_demo_participants=PLAYERS_PER_GROUP,
        app_sequence=["trust_game"],
        demo_mode=True,
    ),
]

if BILENDI_ENABLED:
    SESSION_CONFIGS.append(
        dict(
            name="bilendi",
            display_name="Bilendi — Participant individuel",
            num_demo_participants=PLAYERS_PER_GROUP,
            app_sequence=["dispatcher", "questionnaire", "risk_aversion", "trust_game", "results"],
            bilendi_mode=True,
        ),
    )

SESSION_CONFIG_DEFAULTS = dict(  # Paramètres par défaut appliqués à toutes les sessions
    real_world_currency_per_point=0.50,
    participation_fee=10.00,
    doc="Configuration par défaut pour les sessions de Trust Game AI.",
    demo_mode=False,
)

ROOMS = [  # Configuration des salles d'attente pour les participants
    dict(
        name="econ101",
        display_name="Salle Économie 101",
        participant_label_file="_rooms/econ101.txt",
    ),
    dict(name="live_demo", display_name="Salle de démonstration (sans étiquettes)"),
    dict(name="bilendi", display_name="Bilendi — Étudiants UPJV (panel)"),
]

# =============================================================================
# 4. BILENDI — Intégration panel
# =============================================================================

BILENDI_APP_SEQUENCE = ["questionnaire", "risk_aversion", "trust_game", "results"]
BILENDI_SESSION_CODE = os.getenv("BILENDI_SESSION_CODE", "")
BILENDI_MAX_PARTICIPANTS = int(os.getenv("BILENDI_MAX_PARTICIPANTS", "200"))
BILENDI_RATE_LIMIT = int(os.getenv("BILENDI_RATE_LIMIT", "5"))
BILENDI_RATE_WINDOW = int(os.getenv("BILENDI_RATE_WINDOW", "900"))
BILENDI_ABANDON_TIMEOUT = int(os.getenv("BILENDI_ABANDON_TIMEOUT", "7200"))
BILENDI_RECONNECT_TIMEOUT = int(os.getenv("BILENDI_RECONNECT_TIMEOUT", "300"))  # 5 min

# =============================================================================
# 5. FINANCES — Rémunération des participants
# =============================================================================

SHOW_UP_FEE = 2.5  # Montant fixe payé aux participants pour leur présence

CONVERSION_RATE = 1.0  # Taux de conversion entre les points du jeu et la monnaie réelle

# =============================================================================
# 5. TRUST GAME — Paramètres du jeu de confiance
# =============================================================================

TG_ENDOWMENT = 10  # Dotation initiale des joueurs dans le Trust Game

TG_MULTIPLIER = 3  # Facteur par lequel le montant envoyé par l'expéditeur est multiplié

TG_CHAT_DURATION = 300  # Durée du chat (en secondes) avec l'assistant IA

TG_USER_PREFIX = "<strong>Joueur:</strong> "  # Préfixe affiché devant les messages du joueur dans le chat

TG_BOT_PREFIX = "<strong>Assistant :</strong> "  # Préfixe affiché devant les messages de l'IA dans le chat

TG_CHAT_SEPARATOR = "<br>"  # Séparateur HTML entre les messages du chat

TG_NO_GPT_BEHAVIOR = "Contrôle"  # Label pour la condition sans assistance IA (contrôle)

TG_BEHAVIORS = [
    "Contrôle",
    "Neutre",
    "Altruiste",
    "Égoïste",
]  # Liste des différents comportements possibles de l'IA

TG_MAX_QUIZ_ERRORS = 3  # Nombre maximum d'erreurs autorisées au quiz avant blocage

GPT_BEHAVIOR = os.environ.get(
    "GPT_BEHAVIOR"
)  # Comportement de l'IA récupéré depuis les variables d'environnement

GPT_MODEL = "gpt-5.4-2026-03-05"  # Version du modèle GPT utilisé (ex: gpt-4o)

GPT_SYSTEM_PROMPTS = {  # Instructions (Prompts système) définissant la personnalité de l'IA pour chaque comportement
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
    "Égoïste": (
        "You are an assistant helping a participant in an economic decision task. Briefly "
        "restate the rules of the game, explain the possible consequences of the "
        "participant's decision, and provide a general piece of advice. Emphasize personal "
        "payoff and risk minimization. Do not use emotional pressure. Keep the response "
        "concise. Respond in French."
    ),
}

# =============================================================================
# 6. RISK AVERSION — Mesure de l'aversion au risque
# =============================================================================

RA_ENDOWMENT = 15  # Dotation initiale pour la tâche d'aversion au risque

RA_MAX_INVESTMENT = 5  # Investissement maximum autorisé dans cette tâche

RA_BALL_NUMBER = 60  # Nombre de boules dans l'urne pour le tirage au sort

RA_CONVERSION_RATE = 1.0  # Taux de conversion spécifique pour la tâche de risque

RA_PI_DIGITS = (  # Suite de décimales de Pi
    "141 592 653 589 793 238 462 643 383 279 502 884 197 169 399 375 10"
    "5 820 974 944 592 307 816 406 286 208 998 628 034 825 342 117 067 9"
    "82 148 086 513 282 306 647 093 844 609 550 582 231 725 359 408 128"
    "48 111 745 028 410 270 193 852 110 555 964 462 294 895 493 038 196"
)

RA_FIELD_MAP = {  # Correspondance entre les numéros de décisions et les noms des champs en base de données
    1: "dec_risque_gain",
    2: "dec_ambig_gain",
    3: "dec_risque_perte",
    4: "dec_ambig_perte",
    5: "dec_comp_risque_gain",
    6: "dec_comp_ambig_gain",
    7: "dec_comp_risque_perte",
    8: "dec_comp_ambig_perte",
}

# =============================================================================
# 7. QUESTIONNAIRE — Choix de réponses et métadonnées
# =============================================================================

ORDRES_ETAPES = [
    "Ordre non défini",
    "Q/A/TG",
    "A/Q/TG",
    "Q/TG/A",
]  # Libellés des différents ordres possibles pour les étapes de l'expérience

Q1_CHOICES = [  # Options de réponse pour la fréquence d'utilisation des outils IA
    [1, "Jamais"],
    [2, "Rarement (quelques fois par an)"],
    [3, "Occasionnellement (quelques fois par mois)"],
    [4, "Régulièrement (plusieurs fois par semaine)"],
    [5, "Quotidiennement"],
]

Q3_CHOICES = [  # Options de réponse pour l'ancienneté d'utilisation de l'IA
    [1, "Je n'en utilise pas"],
    [2, "Moins de 6 mois"],
    [3, "Entre 6 mois et 1 an"],
    [4, "Entre 1 et 2 ans"],
    [5, "Plus de 2 ans"],
]

Q4_CHOICES = [  # Options de réponse pour le niveau de formation en IA
    [1, "Non, aucune"],
    [2, "Oui, de manière informelle (articles, vidéos, podcasts)"],
    [3, "Oui, dans le cadre de mes études ou de ma formation professionnelle"],
    [4, "Oui, j'ai suivi une formation dédiée (MOOC, certification, etc.)"],
]

LIKERT_7_CHOICES = [  # Échelle de Likert à 7 points (accord/désaccord)
    [1, "1 - Pas du tout d'accord"],
    [2, "2"],
    [3, "3"],
    [4, "4 - Ni d'accord ni en désaccord"],
    [5, "5"],
    [6, "6"],
    [7, "7 - Tout à fait d'accord"],
]

LIKERT_5_CHOICES = [  # Échelle de Likert à 5 points (accord/désaccord)
    [1, "1 - Pas du tout d'accord"],
    [2, "2"],
    [3, "3"],
    [4, "4 - Ni d'accord ni en désaccord"],
    [5, "5"],
    [6, "6"],
    [7, "7 - Tout à fait d'accord"],
]

Q33_CHOICES = [  # Options pour le genre du participant
    [1, "Femme"],
    [2, "Homme"],
    [3, "Je préfère ne pas répondre"],
]

Q34_CHOICES = [  # Options pour le niveau d'études
    [1, "Brevet des collèges ou moins"],
    [2, "Baccalauréat (ou équivalent)"],
    [3, "Bac+2 / BTS / DUT"],
    [4, "Licence (Bac+3)"],
    [5, "Master (Bac+5)"],
    [6, "Doctorat"],
    [7, "Autre"],
]

Q35_CHOICES = [  # Options pour le domaine d'études
    [1, "Sciences économiques, gestion, finance"],
    [2, "Sciences sociales, psychologie, sociologie"],
    [3, "Sciences exactes, ingénierie, informatique"],
    [4, "Droit, sciences politiques"],
    [5, "Lettres, arts, sciences humaines"],
    [6, "Santé, médecine"],
    [7, "Autre"],
]

Q36_CHOICES = [  # Options pour la tranche de revenus
    [1, "Moins de 1 000 €"],
    [2, "1 000 – 1 999 €"],
    [3, "2 000 – 2 999 €"],
    [4, "3 000 – 3 999 €"],
    [5, "4 000 € et plus"],
    [6, "Je préfère ne pas répondre"],
]

Q37_CHOICES = [  # Options pour le statut professionnel
    [1, "Étudiant(e)"],
    [2, "Salarié(e) du secteur privé"],
    [3, "Salarié(e) du secteur public"],
    [4, "Travailleur(se) indépendant(e) / freelance"],
    [5, "Sans emploi"],
    [6, "Retraité(e)"],
    [7, "Autre"],
]

Q39_CHOICES = (
    [  # Options pour la fréquence de participation à des expériences d'économie
        [1, "Non, jamais"],
        [2, "Oui, une ou deux fois"],
        [3, "Oui, plusieurs fois (3–4 fois)"],
        [4, "Oui, régulièrement (5 fois ou plus)"],
    ]
)

Q40_CHOICES = [  # Options pour la connaissance préalable du Trust Game
    [1, "Non"],
    [2, "Oui, une ou deux fois"],
    [3, "Oui, plusieurs fois"],
]

SVO_CHOICES = [
    [i, str(i)] for i in range(1, 10)
]  # Options pour l'échelle SVO (Social Value Orientation)

# =============================================================================
# 8. CHATGPT (module de test) — Préfixes et configuration du chat
# =============================================================================

CHATGPT_USER_PREFIX = "Joueur : "  # Préfixe utilisateur pour le module de test autonome

CHATGPT_BOT_PREFIX = "Assistant : "  # Préfixe IA pour le module de test autonome

# =============================================================================
# 9. BILENDI — URLs
# =============================================================================

if BILENDI_ENABLED:
    ROOT_URLCONF = "urls"
