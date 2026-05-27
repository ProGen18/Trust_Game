"""
Script de test Bilendi : crée un participant en DB et génère son lien signé.

Usage:
    python test_bilendi_link.py                  # crée test-001 et affiche le lien
    python test_bilendi_link.py mon-id-custom    # avec un ID custom
"""
import hashlib
import hmac
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django
django.setup()

from bilendi.models import BilendiRegistration
import config


def main():
    bilendi_id = sys.argv[1] if len(sys.argv) > 1 else "test-001"

    # 1. Créer/réinitialiser le participant en DB
    reg, created = BilendiRegistration.objects.get_or_create(
        bilendi_id=bilendi_id,
        defaults={"status": "imported"},
    )
    if not created:
        reg.status = "imported"
        reg.participant_code = ""
        reg.save()
        print(f"[OK] Participant {bilendi_id} réinitialisé en 'imported'")
    else:
        print(f"[OK] Participant {bilendi_id} créé")

    # 2. Générer le token signé
    sig = hmac.new(
        config.SECRET_KEY.encode(),
        bilendi_id.encode(),
        hashlib.sha256,
    ).hexdigest()
    token = f"{bilendi_id}:{sig}"

    # 3. Afficher le lien
    print()
    print(f"Lien à ouvrir dans le navigateur :")
    print(f"http://localhost:8000/bilendi/?token={token}")


if __name__ == "__main__":
    main()
