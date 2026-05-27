import hashlib
import hmac
import logging

from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views import View
from otree.models import Session

import config
from .services import validate_and_start

logger = logging.getLogger("bilendi")


class EntryView(View):
    template_name = "bilendi/entry.html"
    error_template = "bilendi/error.html"

    def get(self, request):
        if not config.BILENDI_ENABLED:
            raise Http404
        return render(request, self.template_name)

    def post(self, request):
        if not config.BILENDI_ENABLED:
            raise Http404

        token = request.POST.get("token", "")
        bilendi_id = self._verify_token(token)

        if not bilendi_id:
            logger.warning(
                "bilendi entry REJECTED reason=invalid_token ip=%s",
                request.META.get("REMOTE_ADDR"),
            )
            return render(
                request,
                self.error_template,
                {"message": "Lien invalide ou expiré."},
                status=400,
            )

        session = self._get_bilendi_session()
        if session is None:
            logger.error("bilendi entry FAILED reason=no_session")
            return render(
                request,
                self.error_template,
                {"message": "Service momentanément indisponible."},
                status=503,
            )

        if not validate_and_start(bilendi_id, "pending"):
            logger.warning(
                "bilendi_id=%s REJECTED reason=already_started_or_completed ip=%s",
                bilendi_id,
                request.META.get("REMOTE_ADDR"),
            )
            return render(
                request,
                self.error_template,
                {"message": "Lien invalide ou expiré."},
                status=400,
            )

        request.session["bilendi_id"] = bilendi_id
        request.session["bilendi_session_code"] = session.code

        logger.info(
            "bilendi_id=%s entry OK session=%s", bilendi_id, session.code
        )
        return redirect(f"/join/{session.code}")

    def _verify_token(self, token: str):
        if not token or ":" not in token:
            return None
        try:
            bilendi_id, _, signature = token.rpartition(":")
            expected = hmac.new(
                config.SECRET_KEY.encode(),
                bilendi_id.encode(),
                hashlib.sha256,
            ).hexdigest()
            if hmac.compare_digest(expected, signature):
                return bilendi_id
        except Exception:
            pass
        return None

    def _get_bilendi_session(self):
        code = config.BILENDI_SESSION_CODE
        if not code:
            logger.error("BILENDI_SESSION_CODE not set")
            return None
        sessions = Session.objects_filter()
        for s in sessions:
            if s.code == code:
                return s
        logger.error("Bilendi session not found: code=%s", code)
        return None
