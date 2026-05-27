"""
Endpoints Starlette pour l'intégration Bilendi.

Process Bilendi (selon doc UPJV x Bilendi 2026) :
1. On donne à Bilendi UNE URL unique : https://<site>/bilendi/?ID={ID_ETUDIANT}
2. Bilendi envoie cette URL à chaque étudiant inscrit (avec son ID Bilendi unique)
3. L'étudiant clique → arrive sur /bilendi/?ID=xxx
4. On enregistre l'ID, on le redirige vers la room oTree "bilendi"
5. L'admin oTree assigne une session à la room → l'étudiant joue
6. À la fin, l'université exporte un CSV (ID;gain_euros) via /bilendi/export?key=<token_admin>
7. L'université envoie le CSV à Bilendi → Bilendi envoie les e-chèques

Pas de HMAC : la sécurité repose sur le fait que Bilendi distribue les IDs
nominativement à chaque étudiant.
"""
import csv
import io
import logging
import os

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

import config

logger = logging.getLogger("bilendi")

BILENDI_ROOM_NAME = "bilendi"


_ERROR_HTML = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>Accès refusé</title>
<style>body{{font-family:-apple-system,sans-serif;display:flex;justify-content:center;
align-items:center;min-height:100vh;margin:0;background:#f5f0eb}}
.box{{background:#fff;padding:2.5rem;border-radius:12px;max-width:480px;text-align:center;
box-shadow:0 4px 24px rgba(0,0,0,.08)}}
h1{{color:#c0392b;font-size:1.3rem}}p{{color:#5c4a3a;line-height:1.6}}</style></head>
<body><div class="box"><h1>{title}</h1><p>{message}</p></div></body></html>"""


def _error(title: str, message: str, status: int = 400) -> HTMLResponse:
    return HTMLResponse(
        _ERROR_HTML.format(title=title, message=message),
        status_code=status,
    )


class BilendiEntry(HTTPEndpoint):
    """
    Point d'entrée pour les étudiants envoyés par Bilendi.
    URL: /bilendi/?ID=<id_etudiant_bilendi>
    """

    async def get(self, request: Request):
        if not config.BILENDI_ENABLED:
            return _error("Service désactivé", "Cette URL n'est pas active.", 404)

        # Accepte ID, id, respid (selon configuration Bilendi)
        bilendi_id = (
            request.query_params.get("ID")
            or request.query_params.get("id")
            or request.query_params.get("respid")
            or ""
        ).strip()

        if not bilendi_id:
            return _error(
                "Lien invalide",
                "Aucun identifiant fourni. Vérifiez que vous avez cliqué sur le lien complet reçu par email.",
                400,
            )

        # Crée ou met à jour le BilendiRegistration
        try:
            from bilendi.models import BilendiRegistration
            from django.utils import timezone

            reg, created = BilendiRegistration.objects.get_or_create(
                bilendi_id=bilendi_id,
                defaults={"status": "started", "last_activity_at": timezone.now()},
            )

            if not created:
                if reg.status == "completed":
                    return _error(
                        "Participation déjà enregistrée",
                        "Vous avez déjà terminé cette étude. Votre participation a bien été comptabilisée.",
                        400,
                    )
                # Reprise de session : on rafraîchit l'activité
                reg.last_activity_at = timezone.now()
                if reg.status == "imported":
                    reg.status = "started"
                reg.save(update_fields=["last_activity_at", "status"])

        except Exception as e:
            logger.error("bilendi_id=%s erreur DB: %s", bilendi_id, e)
            return _error(
                "Erreur technique",
                "Une erreur s'est produite. Merci de réessayer dans quelques instants.",
                503,
            )

        # Stocke l'ID dans la session pour le récupérer côté oTree
        request.session["bilendi_id"] = bilendi_id

        logger.info("bilendi_id=%s entrée OK", bilendi_id)

        # Redirige vers la room oTree "bilendi" — la session active y sera affectée
        # par l'admin sans modification de code
        return RedirectResponse(
            f"/room/{BILENDI_ROOM_NAME}?participant_label={bilendi_id}",
            status_code=303,
        )


class BilendiExport(HTTPEndpoint):
    """
    Export CSV des participants Bilendi pour l'envoi à Bilendi.
    URL: /bilendi/export?key=<BILENDI_EXPORT_KEY>

    Format CSV : bilendi_id;status;gain_euros;completed_at
    """

    async def get(self, request: Request):
        if not config.BILENDI_ENABLED:
            return _error("Service désactivé", "Cette URL n'est pas active.", 404)

        # Protection par clé secrète (configurable via env BILENDI_EXPORT_KEY)
        expected_key = os.environ.get("BILENDI_EXPORT_KEY", "")
        provided_key = request.query_params.get("key", "")

        if not expected_key:
            return _error(
                "Configuration incomplète",
                "BILENDI_EXPORT_KEY non défini côté serveur.",
                503,
            )

        if not provided_key or provided_key != expected_key:
            return _error("Accès refusé", "Clé invalide.", 403)

        # Filtre optionnel : ?status=completed (défaut : tout)
        status_filter = request.query_params.get("status")

        try:
            from bilendi.models import BilendiRegistration

            qs = BilendiRegistration.objects.all().order_by("created_at")
            if status_filter:
                qs = qs.filter(status=status_filter)

            buf = io.StringIO()
            writer = csv.writer(buf, delimiter=";")
            writer.writerow(["bilendi_id", "status", "gain_euros", "completed_at"])
            for r in qs:
                gain = (
                    str(r.adjusted_gain) if r.adjusted_gain is not None
                    else (str(r.computed_gain) if r.computed_gain is not None else "")
                )
                completed = r.completed_at.isoformat() if r.completed_at else ""
                writer.writerow([r.bilendi_id, r.status, gain, completed])

            return Response(
                content=buf.getvalue(),
                media_type="text/csv; charset=utf-8-sig",
                headers={
                    "Content-Disposition": 'attachment; filename="bilendi_export.csv"'
                },
            )
        except Exception as e:
            logger.error("Erreur export Bilendi: %s", e)
            return _error("Erreur technique", str(e), 500)
