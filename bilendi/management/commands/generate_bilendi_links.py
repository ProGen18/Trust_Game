"""
Génère les liens signés pour tous les participants Bilendi en statut 'imported'.

Usage:
    python manage.py generate_bilendi_links
    python manage.py generate_bilendi_links --base-url https://mon-serveur.com
    python manage.py generate_bilendi_links --output liens_bilendi.csv
"""
import csv
import hashlib
import hmac
import sys

from django.core.management.base import BaseCommand

import config
from bilendi.models import BilendiRegistration


class Command(BaseCommand):
    help = "Génère les liens signés pour les participants Bilendi (statut imported)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            default=config.LOCAL_URL,
            help="URL de base du serveur (ex: https://mon-serveur.com)",
        )
        parser.add_argument(
            "--output",
            default=None,
            help="Fichier CSV de sortie (défaut: stdout)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Inclure tous les statuts, pas seulement 'imported'",
        )

    def handle(self, *args, **options):
        base_url = options["base_url"].rstrip("/")
        output_file = options["output"]
        include_all = options["all"]

        qs = BilendiRegistration.objects.all()
        if not include_all:
            qs = qs.filter(status="imported")

        if not qs.exists():
            self.stderr.write("Aucun participant trouvé (statut 'imported').")
            self.stderr.write("Utilisez --all pour inclure tous les statuts.")
            sys.exit(1)

        rows = []
        for reg in qs.order_by("created_at"):
            token = self._make_token(reg.bilendi_id)
            link = f"{base_url}/bilendi/?token={token}"
            rows.append({
                "bilendi_id": reg.bilendi_id,
                "status": reg.status,
                "link": link,
            })

        if output_file:
            with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                self._write_csv(f, rows)
            self.stdout.write(
                self.style.SUCCESS(f"{len(rows)} liens écrits dans {output_file}")
            )
        else:
            self._write_csv(sys.stdout, rows)
            self.stderr.write(f"\n{len(rows)} liens générés.")

    def _make_token(self, bilendi_id: str) -> str:
        sig = hmac.new(
            config.SECRET_KEY.encode(),
            bilendi_id.encode(),
            hashlib.sha256,
        ).hexdigest()
        return f"{bilendi_id}:{sig}"

    def _write_csv(self, out, rows):
        writer = csv.DictWriter(
            out,
            fieldnames=["bilendi_id", "status", "link"],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(rows)
