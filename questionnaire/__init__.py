from otree.api import *
from datetime import datetime
import config

class C(BaseConstants):
    """Constantes et options de réponses pour le questionnaire."""
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

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Metadonnées
    date = models.StringField(doc="Date de passation de l'expérience.")
    ordre_etapes = models.StringField(doc="Ordre des applications pour ce participant.")
    session_group = models.IntegerField(initial=0, doc="ID du groupe de session.")
    player_name = models.StringField(blank=True)
    go_back = models.BooleanField(initial=False, doc="Indicateur de navigation arrière.")

    # ==== PARTIE 1 ====
    q1 = models.IntegerField(label="Q1. À quelle fréquence utilisez-vous des outils basés sur l'intelligence artificielle (ChatGPT, Copilot, Gemini, Mistral, Claude, etc.) ?", choices=C.Q1_CHOICES, widget=widgets.RadioSelect)
    
    # Q2 Checkboxes
    q2_travail = models.BooleanField(label="Travail / vie professionnelle", blank=True, widget=widgets.CheckboxInput)
    q2_etudes = models.BooleanField(label="Études ou formation", blank=True, widget=widgets.CheckboxInput)
    q2_redaction = models.BooleanField(label="Rédaction et aide à l'écriture", blank=True, widget=widgets.CheckboxInput)
    q2_recherche = models.BooleanField(label="Recherche d'informations", blank=True, widget=widgets.CheckboxInput)
    q2_programmation = models.BooleanField(label="Programmation / développement informatique", blank=True, widget=widgets.CheckboxInput)
    q2_loisirs = models.BooleanField(label="Loisirs et créativité (image, musique, jeux…)", blank=True, widget=widgets.CheckboxInput)
    q2_decision = models.BooleanField(label="Prise de décision personnelle (achats, santé, voyage…)", blank=True, widget=widgets.CheckboxInput)
    q2_aucun = models.BooleanField(label="Je n'en utilise pas", blank=True, widget=widgets.CheckboxInput)

    q3 = models.IntegerField(label="Q3. Depuis combien de temps utilisez-vous ce type d'outil ?", choices=C.Q3_CHOICES, widget=widgets.RadioSelect)
    q4 = models.IntegerField(label="Q4. Avez-vous suivi une formation ou lu des ressources spécifiques sur le fonctionnement de l'IA ?", choices=C.Q4_CHOICES, widget=widgets.RadioSelect)

    # Q5 Checkboxes
    q5_chatgpt = models.BooleanField(label="ChatGPT (OpenAI)", blank=True, widget=widgets.CheckboxInput)
    q5_copilot = models.BooleanField(label="Copilot (Microsoft)", blank=True, widget=widgets.CheckboxInput)
    q5_gemini = models.BooleanField(label="Gemini (Google)", blank=True, widget=widgets.CheckboxInput)
    q5_claude = models.BooleanField(label="Claude (Anthropic)", blank=True, widget=widgets.CheckboxInput)
    q5_mistral = models.BooleanField(label="Mistral / Le Chat", blank=True, widget=widgets.CheckboxInput)
    q5_perplexity = models.BooleanField(label="Perplexity AI", blank=True, widget=widgets.CheckboxInput)
    q5_integre = models.BooleanField(label="Un outil IA intégré à un logiciel métier (ex. : suite Office, outil de design, CRM…)", blank=True, widget=widgets.CheckboxInput)
    q5_aucun = models.BooleanField(label="Aucun de ces outils", blank=True, widget=widgets.CheckboxInput)

    # ==== PARTIE 2 ====
    q6 = models.IntegerField(label="Q6. Je fais généralement confiance aux informations fournies par les outils d'IA.", choices=C.LIKERT_7_CHOICES, widget=widgets.RadioSelectHorizontal)
    q7 = models.IntegerField(label="Q7. Les outils d'IA me semblent fiables pour m'aider à prendre des décisions importantes.", choices=C.LIKERT_7_CHOICES, widget=widgets.RadioSelectHorizontal)
    q8 = models.IntegerField(label="Q8. Je pense que les outils d'IA peuvent facilement se tromper ou donner de mauvais conseils. (R)", choices=C.LIKERT_7_CHOICES, widget=widgets.RadioSelectHorizontal)
    q9 = models.IntegerField(label="Q9. Je me sens à l'aise à l'idée de laisser une IA influencer certaines de mes décisions.", choices=C.LIKERT_7_CHOICES, widget=widgets.RadioSelectHorizontal)
    q10 = models.IntegerField(label="Q10. Je vérifie systématiquement les réponses d'une IA avant d'agir en conséquence. (R)", choices=C.LIKERT_7_CHOICES, widget=widgets.RadioSelectHorizontal)
    q11 = models.IntegerField(label="Q11. Je considère que les outils d'IA actuels sont globalement compétents dans tâches pour lesquelles ils sont conçus.", choices=C.LIKERT_7_CHOICES, widget=widgets.RadioSelectHorizontal)
    q12 = models.IntegerField(label="Q12. Je pense que les systèmes d'IA sont suffisamment transparents sur leur fonctionnement et leurs limites.", choices=C.LIKERT_7_CHOICES, widget=widgets.RadioSelectHorizontal)

    # ==== PARTIE 3 ====
    q13 = models.IntegerField(label="Q13. L'essor de l'IA me préoccupe pour l'avenir de l'emploi.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q14 = models.IntegerField(label="Q14. Je crains que les outils d'IA ne soient utilisés pour manipuler les comportements humains.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q15 = models.IntegerField(label="Q15. Je pense que les IA reproduisent des biais qui les rendent injustes envers certains groupes de personnes.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q16 = models.IntegerField(label="Q16. L'utilisation généralisée de l'IA dans la société me rend globalement mal à l'aise.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q17 = models.IntegerField(label="Q17. Je m'inquiète de l'impact de l'IA sur la protection de ma vie privée et de mes données personnelles.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q18 = models.IntegerField(label="Q18. Je me sens capable de détecter quand une IA essaie d'orienter mes choix ou mes opinions.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q19 = models.IntegerField(label="Q19. Je crains que le recours croissant à l'IA ne réduise progressivement notre capacité à penser et décider par nous-mêmes.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)

    # ==== PARTIE 4 (SVO) ====
    svo_item_1 = models.IntegerField(choices=C.SVO_CHOICES, widget=widgets.RadioSelect)
    svo_item_2 = models.IntegerField(choices=C.SVO_CHOICES, widget=widgets.RadioSelect)
    svo_item_3 = models.IntegerField(choices=C.SVO_CHOICES, widget=widgets.RadioSelect)
    svo_item_4 = models.IntegerField(choices=C.SVO_CHOICES, widget=widgets.RadioSelect)
    svo_item_5 = models.IntegerField(choices=C.SVO_CHOICES, widget=widgets.RadioSelect)
    svo_item_6 = models.IntegerField(choices=C.SVO_CHOICES, widget=widgets.RadioSelect)

    # ==== PARTIE 5 ====
    q20 = models.IntegerField(label="Q20. Si quelqu'un me rend service, je fais tout mon possible pour lui rendre la pareille, même si cela me prend du temps ou me coûte quelque chose.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q21 = models.IntegerField(label="Q21. Je m'efforce d'aider les personnes qui m'ont aidé par le passé, même lorsque cela représente un effort de ma part.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q22 = models.IntegerField(label="Q22. Si quelqu'un me cause du tort intentionnellement, je cherche à rétablir l'équité, même si cela a un coût pour moi.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q23 = models.IntegerField(label="Q23. Lorsque quelqu'un m'a traité injustement, je cherche à lui faire comprendre que ce comportement a des conséquences.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q24 = models.IntegerField(label="Q24. Je fais volontiers confiance à un inconnu, même sans aucune garantie de sa part.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q25 = models.IntegerField(label="Q25. Je préfère renoncer à un gain personnel plutôt que de profiter d'une situation au détriment d'une autre personne.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)

    # ==== PARTIE 6 ====
    q26 = models.IntegerField(label="Q26. En général, on peut faire confiance aux gens.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q27 = models.IntegerField(label="Q27. La plupart des gens essaient d'être honnêtes dans leurs rapports aux autres.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q28 = models.IntegerField(label="Q28. On ne peut jamais être trop prudent dans ses relations avec les autres. (R)", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q29 = models.IntegerField(label="Q29. La plupart des gens profiteraient de vous si l'occasion se présentait. (R)", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q30 = models.IntegerField(label="Q30. La plupart des gens respectent les règles et les normes sociales même lorsque personne ne les surveille.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)
    q31 = models.IntegerField(label="Q31. Je pense que la majorité des gens ont de bonnes intentions envers autrui.", choices=C.LIKERT_5_CHOICES, widget=widgets.RadioSelectHorizontal)

    # ==== PARTIE 7 ====
    q32 = models.IntegerField(label="Q32. Quel est votre âge ? (en années)")
    q33 = models.IntegerField(label="Q33. Quel est votre genre ?", choices=C.Q33_CHOICES, widget=widgets.RadioSelect)
    q34 = models.IntegerField(label="Q34. Quel est votre niveau d'études le plus élevé obtenu ?", choices=C.Q34_CHOICES, widget=widgets.RadioSelect)
    q35 = models.IntegerField(label="Q35. Dans quel domaine avez-vous principalement étudié ou travaillez-vous ?", choices=C.Q35_CHOICES, widget=widgets.RadioSelect)
    q35_autre = models.StringField(blank=True, label="Autre domaine :")
    q36 = models.IntegerField(label="Q36. Dans quelle tranche se situe votre revenu mensuel net personnel (en euros) ?", choices=C.Q36_CHOICES, widget=widgets.RadioSelect)
    q37 = models.IntegerField(label="Q37. Quelle est votre situation professionnelle actuelle ?", choices=C.Q37_CHOICES, widget=widgets.RadioSelect)
    q38 = models.StringField(label="Q38. Dans quel pays résidez-vous actuellement ?")
    q39 = models.IntegerField(label="Q39. Avez-vous déjà participé à une expérience économique (Jeu experimental, dilemme du prisonnier, jeu de l'ultimatum…) ?", choices=C.Q39_CHOICES, widget=widgets.RadioSelect)
    q40 = models.IntegerField(label="Q40. Avez-vous déjà participé spécifiquement à un Jeu experimental (Trust Game) avant aujourd'hui ?", choices=C.Q40_CHOICES, widget=widgets.RadioSelect)


# ==== PAGES ====

class Welcome(Page):
    def before_next_page(player, timeout_happened):
        config_name = player.session.config.get("name", "")
        if config_name == "groupe_1":
            n = 1
        elif config_name == "groupe_2":
            n = 2
        elif config_name == "groupe_3":
            n = 3
        else:
            n = 0
        player.ordre_etapes = C.ORDRES_ETAPES[n]
        player.session_group = n
        player.date = datetime.now().strftime("%d-%b-%y")
        player.participant.vars["show_up_fee"] = C.SHOW_UP_FEE

def go_back_live_method(player, data):
    if data.get('go_back'):
        if player._index_in_pages > 1:
            player._index_in_pages -= 1
        return {player.id_in_group: {'go_back_success': True}}

class Part1(Page):
    live_method = go_back_live_method
    form_model = "player"
    form_fields = [
        "q1", 
        "q2_travail", "q2_etudes", "q2_redaction", "q2_recherche", "q2_programmation", "q2_loisirs", "q2_decision", "q2_aucun",
        "q3", "q4",
        "q5_chatgpt", "q5_copilot", "q5_gemini", "q5_claude", "q5_mistral", "q5_perplexity", "q5_integre", "q5_aucun"
    ]
    def before_next_page(player, timeout_happened):
        if player.go_back:
            player._index_in_pages -= 2
            player.go_back = False

class Part2(Page):
    live_method = go_back_live_method
    form_model = "player"
    form_fields = ["q6", "q7", "q8", "q9", "q10", "q11", "q12"]
    def before_next_page(player, timeout_happened):
        if player.go_back:
            player._index_in_pages -= 2
            player.go_back = False

class Part3(Page):
    live_method = go_back_live_method
    form_model = "player"
    form_fields = ["q13", "q14", "q15", "q16", "q17", "q18", "q19"]
    def before_next_page(player, timeout_happened):
        if player.go_back:
            player._index_in_pages -= 2
            player.go_back = False

class Part4(Page):
    live_method = go_back_live_method
    form_model = "player"
    form_fields = ["svo_item_1", "svo_item_2", "svo_item_3", "svo_item_4", "svo_item_5", "svo_item_6"]
    def before_next_page(player, timeout_happened):
        if player.go_back:
            player._index_in_pages -= 2
            player.go_back = False

class Part5(Page):
    live_method = go_back_live_method
    form_model = "player"
    form_fields = ["q20", "q21", "q22", "q23", "q24", "q25"]
    def before_next_page(player, timeout_happened):
        if player.go_back:
            player._index_in_pages -= 2
            player.go_back = False

class Part6(Page):
    live_method = go_back_live_method
    form_model = "player"
    form_fields = ["q26", "q27", "q28", "q29", "q30", "q31"]
    def before_next_page(player, timeout_happened):
        if player.go_back:
            player._index_in_pages -= 2
            player.go_back = False

class Part7(Page):
    live_method = go_back_live_method
    form_model = "player"
    form_fields = ["q32", "q33", "q34", "q35", "q35_autre", "q36", "q37", "q38", "q39", "q40"]
    def before_next_page(player, timeout_happened):
        if player.go_back:
            player._index_in_pages -= 2
            player.go_back = False

class Login(Page):
    form_model = "player"
    form_fields = ["player_name"]

class Conclusion(Page):
    pass

page_sequence = [
    Welcome,
    Part1,
    Part2,
    Part3,
    Part4,
    Part5,
    Part6,
    Part7,
    Conclusion,
]
