"""
Script de gestion Bilendi (migrations Django + utilitaires).

Usage local:
    python manage_bilendi.py migrate       # crée/met à jour la table BilendiRegistration
    python manage_bilendi.py list          # liste tous les participants
    python manage_bilendi.py export        # export CSV vers stdout

Usage Heroku (release):
    Le Procfile lance automatiquement `python manage_bilendi.py migrate`
    après chaque déploiement.
"""
import csv
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django
django.setup()


def cmd_migrate():
    from django.core.management import call_command
    call_command("makemigrations", "bilendi", verbosity=0)
    call_command("migrate", "bilendi", verbosity=1)


def cmd_list():
    from bilendi.models import BilendiRegistration
    qs = BilendiRegistration.objects.all().order_by("created_at")
    print(f"{'bilendi_id':<25} {'status':<12} {'gain':<8}")
    print("-" * 50)
    for r in qs:
        gain = (
            str(r.adjusted_gain) if r.adjusted_gain is not None
            else (str(r.computed_gain) if r.computed_gain is not None else "-")
        )
        print(f"{r.bilendi_id:<25} {r.status:<12} {gain:<8}")


def cmd_export():
    from bilendi.models import BilendiRegistration
    w = csv.writer(sys.stdout, delimiter=";")
    w.writerow(["bilendi_id", "status", "gain_euros", "completed_at"])
    for r in BilendiRegistration.objects.all().order_by("created_at"):
        gain = (
            str(r.adjusted_gain) if r.adjusted_gain is not None
            else (str(r.computed_gain) if r.computed_gain is not None else "")
        )
        w.writerow([
            r.bilendi_id, r.status, gain,
            r.completed_at.isoformat() if r.completed_at else "",
        ])


COMMANDS = {"migrate": cmd_migrate, "list": cmd_list, "export": cmd_export}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "migrate"
    if cmd not in COMMANDS:
        print(f"Commandes disponibles : {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[cmd]()
