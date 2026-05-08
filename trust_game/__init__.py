"""
Module pour le Trust Game (Jeu de Confiance) avec intégration d'un assistant IA (GPT).
Ce module gère la logique du jeu, la communication entre les joueurs et l'interaction avec l'API OpenAI.
"""

from otree.api import *
import random
import time
import config


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


class Subsession(BaseSubsession):
    """Gère la création de la session et l'attribution des options de chat au démarrage."""

    def creating_session(self):
        """Initialisation des paramètres spécifiques pour chaque joueur au début de la session."""
        demo_mode = self.session.config.get("demo_mode", False)
        for player in self.get_players():
            set_chat_options(player)
            if demo_mode:
                player.popup_accepted = True
                set_partner_id(player)
                if player.id_in_group == 1 and player.gpt_behavior == C.NO_GPT_BEHAVIOR:
                    player.gpt_behavior = "Neutre"


class Group(BaseGroup):
    """Représente un groupe de deux joueurs (A et B) et gère les données partagées."""

    amount_sent = models.CurrencyField(
        min=0, max=C.ENDOWMENT, doc="Montant envoyé par le Joueur A au Joueur B."
    )
    amount_sent_back = models.CurrencyField(
        doc="Montant renvoyé par le Joueur B au Joueur A."
    )
    talk_time = models.IntegerField(
        doc="Durée effective de la communication en secondes."
    )
    expire_time = models.FloatField(doc="Timestamp d'expiration de la session de chat.")

    def set_payoffs(self):
        """Calcule les gains finaux pour les deux membres du groupe à la fin du jeu."""
        sent = self.amount_sent
        sent_back = self.amount_sent_back
        tripled = sent * C.MULTIPLIER

        p1: Player = self.get_player_by_id(1)
        p2: Player = self.get_player_by_id(2)

        p1.payoff = C.ENDOWMENT - sent + sent_back
        p2.payoff = tripled - sent_back


class Player(BasePlayer):
    """Contient les données individuelles d'un participant et ses réponses au questionnaire/quiz."""

    tg_role = models.StringField(doc="Rôle dans le jeu (A ou B).")
    partner_id = models.StringField(doc="Identifiant interne du partenaire de jeu.")
    error_count = models.IntegerField(
        initial=0, doc="Nombre d'erreurs commises lors du quiz de compréhension."
    )

    # Champs du quiz de compréhension
    q1_b_receive = models.IntegerField(label="")
    q2_a_get_back = models.IntegerField(label="")
    q3_a_final = models.IntegerField(label="")
    q3_b_final = models.IntegerField(label="")
    q4_true_false = models.StringField(
        label="", choices=["Vrai", "Faux"], widget=widgets.RadioSelect
    )

    # Variables dynamiques pour les questions du quiz
    x = models.IntegerField()
    y = models.IntegerField()
    z = models.IntegerField()

    # Historique et état de la communication
    message = models.LongStringField(blank=True)
    gpt_history = models.LongStringField(
        initial="", doc="Historique HTML de la discussion avec l'IA."
    )

    gpt_behavior = models.StringField(
        initial=C.GPT_BEHAVIOR, doc="Comportement assigné à l'assistant GPT."
    )
    popup_accepted = models.BooleanField(
        initial=False, doc="Indique si le joueur a validé la popup IA."
    )
    participant_left = models.BooleanField(
        initial=False, doc="Indique si le partenaire a quitté la session prématurément."
    )


def set_participant_vars(player: Player):
    """
    Archive les données du jeu dans participant.vars pour une utilisation inter-applications.
    Cette fonction est appelée à la fin du module pour alimenter la page de résultats globaux.
    """
    player.tg_role = "A" if player.id_in_group == 1 else "B"
    player.participant.vars["tg_role"] = player.tg_role
    player.participant.vars["tg_endowment"] = C.ENDOWMENT

    group: Group = player.group
    sent = int(group.field_maybe_none("amount_sent") or 0)
    tripled = sent * C.MULTIPLIER
    sent_back = int(group.field_maybe_none("amount_sent_back") or 0)
    player.participant.vars["tg_sent"] = sent
    player.participant.vars["tg_multiplier"] = C.MULTIPLIER
    player.participant.vars["tg_sent_back"] = sent_back


def set_partner_id(player: Player):
    """Identifie et stocke l'ID ou le code du partenaire de jeu."""
    partner = player.get_others_in_group()[0]
    uid = partner.participant.code
    id = str(partner.participant.id_in_session)
    player.partner_id = uid if uid else id


def set_chat_options(player: Player):
    """
    Attribue dynamiquement un traitement (Contrôle ou type d'IA).

    Logique de rotation et répartition :
      - Rotation par paires : chaque paire de participants consécutifs reçoit le même comportement GPT.
    """
    behaviors = C.BEHAVIORS
    nb_behaviors = len(behaviors)
    participant_id = player.participant.id_in_session
    index = ((participant_id - 1) // 2) % nb_behaviors
    player.gpt_behavior = behaviors[index]


class BaseQuiz(Page):
    """Classe de base pour les pages de quiz, gérant les champs du formulaire et les variables dynamiques."""

    form_model = "player"
    form_fields = [
        "q1_b_receive",
        "q2_a_get_back",
        "q3_a_final",
        "q3_b_final",
        "q4_true_false",
    ]

    @staticmethod
    def vars_for_template(player: Player):
        """Génère des valeurs aléatoires pour personnaliser les questions du quiz pour chaque joueur."""
        player.x = random.randint(2, 10)

        mult = C.MULTIPLIER
        max_choice = mult * C.ENDOWMENT
        choice_list = [x for x in range(mult, max_choice + 1) if x % mult == 0]
        player.y = random.choice(choice_list)

        player.z = random.randint(1, player.y)
        return {
            "participant": player.participant,
            "x": player.x,
            "y": player.y,
            "z": player.z,
        }

    @staticmethod
    def error_message(player: Player, values):
        """Valide les réponses et renvoie des messages d'erreur explicatifs ou génériques selon le nombre d'échecs."""
        errors = {}
        correct_q1 = player.x * C.MULTIPLIER

        if values["q1_b_receive"] != correct_q1:
            player.error_count += 1
            if player.error_count < C.MAX_QUIZ_ERRORS:
                errors["q1_b_receive"] = (
                    f"Le joueur B reçoit {player.x}€ × {C.MULTIPLIER} = {correct_q1}€."
                )
            else:
                errors["q1_b_receive"] = "Réponse incorrecte. Relisez les instructions."

        if values["q2_a_get_back"] != player.z:
            player.error_count += 1
            if player.error_count < C.MAX_QUIZ_ERRORS:
                errors["q2_a_get_back"] = (
                    f"Le joueur A reçoit ce que B renvoie : {player.z}€."
                )
            else:
                errors["q2_a_get_back"] = (
                    "Réponse incorrecte. Relisez les instructions."
                )

        if values["q3_a_final"] != 4:
            player.error_count += 1
            if player.error_count < C.MAX_QUIZ_ERRORS:
                errors["q3_a_final"] = "Revoir le calcul : 5€ - 2€ + 1€ = 4€."
            else:
                errors["q3_a_final"] = "Réponse incorrecte. Relisez les instructions."

        if values["q3_b_final"] != 5:
            player.error_count += 1
            if player.error_count < C.MAX_QUIZ_ERRORS:
                errors["q3_b_final"] = "Revoir le calcul : 6€ - 1€ = 5€."
            else:
                errors["q3_b_final"] = "Réponse incorrecte. Relisez les instructions."

        if values["q4_true_false"] != "Faux":
            player.error_count += 1
            if player.error_count < C.MAX_QUIZ_ERRORS:
                errors["q4_true_false"] = (
                    "C'est faux : le montant renvoyé par B n'est pas triplé."
                )
            else:
                errors["q4_true_false"] = (
                    "Réponse incorrecte. Relisez les instructions."
                )

        return errors or None


class QuizExample1(BaseQuiz):

    @staticmethod
    def is_displayed(player: Player):
        return not player.session.config.get("demo_mode", False)
    pass


class Instructions(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return {
            "gpt behavior": player.gpt_behavior,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_partner_id(player)

    @staticmethod
    def is_displayed(player: Player):
        return not player.session.config.get("demo_mode", False)


def chat_with_gpt(player: Player, data: dict):
    """
    Gère l'interaction avec l'API OpenAI (GPT) pour simuler un assistant conseil.
    Conserve le contexte de la discussion et respecte le tempérament assigné au joueur.
    """
    user_message = data["message"]

    system_prompt = config.GPT_SYSTEM_PROMPTS.get(
        player.gpt_behavior,
        "Tu réponds en une à deux phrases simples. Respond in French.",
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


def handle_amount_sent(player: Player, data: dict) -> dict:
    """Transfère les jetons du Joueur A au Joueur B et déclenche la notification temps réel."""
    amount = int(data["amount_sent"])
    group: Group = player.group
    demo_mode = player.session.config.get("demo_mode", False)

    if 0 <= amount <= C.ENDOWMENT:
        group.amount_sent = amount
        if group.field_maybe_none("expire_time") is None:
            group.expire_time = time.time() + C.CHAT_DURATION
        group.talk_time = int(C.CHAT_DURATION - (group.expire_time - time.time()))

        responses = {}
        for p in group.get_players():
            if p.id_in_group == 1:
                responses[p.id_in_group] = {
                    "status": "sent",
                    "amount_sent": amount,
                }
            else:
                responses[p.id_in_group] = {
                    "status": "received",
                    "amount_sent": amount,
                    "tripled_amount": int(amount * C.MULTIPLIER),
                }

        if demo_mode:
            tripled = int(amount * C.MULTIPLIER)
            amount_back = random.randint(0, tripled)
            group.amount_sent_back = amount_back
            group.set_payoffs()
            responses[1].update({
                "status": "complete",
                "can_proceed": True,
                "amount_sent": amount,
                "amount_sent_back": amount_back,
                "tripled_amount": tripled,
            })

        return responses


def handle_amount_sent_back(player: Player, data: dict) -> dict:
    """Consigne le renvoi de jetons par le Joueur B et clôture la transaction."""
    group: Group = player.group
    amount_back = int(data["amount_sent_back"])
    tripled_amount = int(group.amount_sent * C.MULTIPLIER)

    if 0 <= amount_back <= tripled_amount:
        group.amount_sent_back = amount_back

        responses = {}
        for p in group.get_players():
            responses[p.id_in_group] = {
                "status": "complete",
                "can_proceed": True,
                "amount_sent": group.amount_sent,
                "amount_sent_back": amount_back,
                "tripled_amount": tripled_amount,
            }
        group.set_payoffs()  # Mise à jour des payoffs définitifs
        return responses


class SyncWaitPage(WaitPage):

    @staticmethod
    def after_all_players_arrive(group: Group):
        pass

    @staticmethod
    def is_displayed(player: Player):
        return not player.session.config.get("demo_mode", False)

    @staticmethod
    def vars_for_template(player: Player):
        other_player = player.get_others_in_group()[0]
        other_participant_number = other_player.participant.id_in_session
        return {
            "other_player": other_player,
            "other_participant_number": other_participant_number,
        }


class GamePlay(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.session.config.get("demo_mode", False):
            return player.id_in_group == 1
        return True

    @staticmethod
    def vars_for_template(player: Player):
        demo_mode = player.session.config.get("demo_mode", False)
        # En démo, expire_time est initialisé seulement après la séquence
        # pédagogique côté client (via liveSend({demo_complete: true})),
        # afin que le chrono ne grignote pas le temps réel de jeu pendant la démo.
        return {
            "has_chat_gpt": player.gpt_behavior != C.NO_GPT_BEHAVIOR,
            "gpt_behavior": player.gpt_behavior,
            "gpt_history": player.gpt_history,
            "demo_mode": demo_mode,
        }

    @staticmethod
    def live_method(player: Player, data):
        if "is_chat_gpt" in data:
            return chat_with_gpt(player, data)

        # Gestion de l'acceptation de la popup OU fin de la démo interactive
        if "popup_accepted" in data or "demo_complete" in data:
            player.popup_accepted = True
            group = player.group
            demo = player.session.config.get("demo_mode", False)
            # En mode démo, seul le Joueur A est réellement présent ; on démarre
            # immédiatement le chrono pour lui, sans attendre le partenaire virtuel.
            if demo:
                if group.field_maybe_none("expire_time") is None:
                    group.expire_time = time.time() + C.CHAT_DURATION
                return {player.id_in_group: {"start_timer": group.expire_time}}
            # Mode normal : on attend que les deux joueurs aient validé la popup.
            if all(p.popup_accepted for p in group.get_players()):
                if group.field_maybe_none("expire_time") is None:
                    group.expire_time = time.time() + C.CHAT_DURATION
                    return {
                        p.id_in_group: {"start_timer": group.expire_time}
                        for p in group.get_players()
                    }
            return None

        # envoi de jetons par le joueur A
        if "amount_sent" in data and player.id_in_group == 1:
            return handle_amount_sent(player, data)

        # renvoi de jetons par le joueur B
        if "amount_sent_back" in data and player.id_in_group == 2:
            return handle_amount_sent_back(player, data)

        # heartbeat : le client envoie {"ping": true} toutes les 30s
        if "ping" in data:
            responses = {}
            for p in player.group.get_players():
                if p.id_in_group != player.id_in_group:
                    responses[p.id_in_group] = {"partner_alive": True}
            return responses

        # le client signale qu'il quitte (beforeunload)
        if "leaving" in data:
            demo = player.session.config.get("demo_mode", False)
            if demo:
                return None
            responses = {}
            for p in player.group.get_players():
                if p.id_in_group != player.id_in_group:
                    p.participant_left = True
                    responses[p.id_in_group] = {"partner_left": True}
            return responses

        return None

    @staticmethod
    def js_vars(player: Player):
        group: Group = player.group
        return {
            "id_in_group": player.id_in_group,
            "endowment": C.ENDOWMENT,
            "multiplier": C.MULTIPLIER,
            "amount_sent": group.field_maybe_none("amount_sent"),
            "amount_sent_back": group.field_maybe_none("amount_sent_back"),
            "expire_time": group.field_maybe_none("expire_time") or 0,
            "demo_mode": player.session.config.get("demo_mode", False),
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """
        Si le timer expire sans que les jetons aient été échangés,
        on fixe des valeurs par défaut pour ne pas bloquer le partenaire.
        - Joueur A : amount_sent = 0
        - Joueur B : amount_sent_back = 0
        Les gains sont ensuite calculés (payoff nul pour le joueur fautif).
        """
        if timeout_happened:
            group: Group = player.group
            if (
                player.id_in_group == 1
                and group.field_maybe_none("amount_sent") is None
            ):
                group.amount_sent = 0
                group.amount_sent_back = 0
                group.talk_time = C.CHAT_DURATION
                group.set_payoffs()
            elif (
                player.id_in_group == 2
                and group.field_maybe_none("amount_sent_back") is None
            ):
                group.amount_sent_back = 0
                group.set_payoffs()


class Results(Page):
    """Page finale affichant le bilan de la transaction de confiance pour chaque joueur."""

    @staticmethod
    def is_displayed(player: Player):
        return True

    @staticmethod
    def vars_for_template(player: Player):
        """Récupère les montants réels du groupe pour l'affichage final (avec sécurité anti-null)."""
        group: Group = player.group
        sent = int(group.field_maybe_none("amount_sent") or 0)
        sent_back = int(group.field_maybe_none("amount_sent_back") or 0)
        tripled = sent * C.MULTIPLIER
        return dict(
            sent=sent,
            sent_back=sent_back,
            tripled=tripled,
            payoff=int(player.payoff),
            is_test_round=(player.round_number == 1),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """Sauvegarde les résultats du TG dans les variables globales du participant."""
        set_participant_vars(player)


page_sequence = [
    Instructions,
    QuizExample1,
    SyncWaitPage,
    GamePlay,
    Results,
]
