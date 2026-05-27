"""
Affiche le statut de tous les participants Bilendi en DB.

Usage:
    python bilendi_status.py              # liste tous
    python bilendi_status.py completed    # filtre par statut
    python bilendi_status.py reset <id>   # remet un participant en 'imported'
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django
django.setup()

from bilendi.models import BilendiRegistration


def list_all(status_filter=None):
    qs = BilendiRegistration.objects.all().order_by("created_at")
    if status_filter:
        qs = qs.filter(status=status_filter)

    if not qs.exists():
        print("Aucun participant trouvé.")
        return

    print(f"{'bilendi_id':<25} {'status':<12} {'gain':<8} {'participant':<12}")
    print("-" * 60)
    for r in qs:
        gain = str(r.computed_gain) if r.computed_gain else "-"
        pc = r.participant_code or "-"
        print(f"{r.bilendi_id:<25} {r.status:<12} {gain:<8} {pc:<12}")
    print(f"\nTotal: {qs.count()}")


def reset(bilendi_id):
    try:
        r = BilendiRegistration.objects.get(bilendi_id=bilendi_id)
        r.status = "imported"
        r.participant_code = ""
        r.save()
        print(f"[OK] {bilendi_id} remis en 'imported'")
    except BilendiRegistration.DoesNotExist:
        print(f"[ERREUR] {bilendi_id} introuvable")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "reset":
        reset(sys.argv[2])
    elif len(sys.argv) >= 2:
        list_all(status_filter=sys.argv[1])
    else:
        list_all()
