import logging
import re

from django.http import HttpResponseForbidden

logger = logging.getLogger("bilendi")

OTREE_PAGE_RE = re.compile(r"^/p/[a-z0-9]+/\d+/")


class BilendiValidationMiddleware:
    """Vérifie la correspondance entre l'ID Bilendi en session Django
    et le bilendi_id stocké dans le participant oTree.

    Ne s'exécute que sur les URLs de page oTree (/p/...).
    Ignore les requêtes sans bilendi_id en session Django.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path

        if not OTREE_PAGE_RE.match(path):
            return None

        session_bilendi_id = request.session.get("bilendi_id")
        if not session_bilendi_id:
            return None

        try:
            participant_code = view_kwargs.get("participant_code")
            if not participant_code:
                return None

            from otree.models import Participant
            participant = Participant.objects.filter(code=participant_code).first()
            if participant is None:
                logger.warning(
                    "bilendi middleware: participant not found code=%s", participant_code
                )
                return HttpResponseForbidden("Participant non trouvé.")

            if participant.vars.get("bilendi_id") != session_bilendi_id:
                logger.warning(
                    "bilendi middleware: mismatch session=%s participant=%s",
                    session_bilendi_id,
                    participant.vars.get("bilendi_id"),
                )
                return HttpResponseForbidden("Accès non autorisé.")
        except Exception as e:
            logger.error("bilendi middleware error: %s", e)
            return None

        return None
