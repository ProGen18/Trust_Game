import logging
from django.db import transaction
from django.utils import timezone
import config

logger = logging.getLogger("bilendi")


def compute_total_gain(participant):
    show_up = float(config.SHOW_UP_FEE)
    risk = float(participant.vars.get("total_risk_aversion", 0))
    tg = float(participant.vars.get("tg_gain", 0))
    return round(show_up + risk + tg, 2)


def validate_and_start(bilendi_id: str, participant_code: str):
    with transaction.atomic():
        from .models import BilendiRegistration
        updated = (
            BilendiRegistration.objects
            .select_for_update()
            .filter(bilendi_id=bilendi_id, status="imported")
            .update(
                status="started",
                participant_code=participant_code,
                last_activity_at=timezone.now(),
            )
        )
        if updated != 1:
            return False
        logger.info("bilendi_id=%s status imported→started", bilendi_id)
    return True


def complete_participant(participant):
    bilendi_id = participant.vars.get("bilendi_id")
    if not bilendi_id:
        return

    from .models import BilendiRegistration
    gain = compute_total_gain(participant)
    tg_skipped = participant.vars.get("trust_game_skipped", False)
    updated = (
        BilendiRegistration.objects
        .filter(bilendi_id=bilendi_id, status="started")
        .update(
            status="completed",
            computed_gain=gain,
            trust_game_skipped=tg_skipped,
            completed_at=timezone.now(),
            last_activity_at=timezone.now(),
        )
    )
    if updated:
        participant.vars["bilendi_status"] = "completed"
        logger.info("bilendi_id=%s status started→completed gain=%s tg_skipped=%s",
                    bilendi_id, gain, tg_skipped)
    else:
        logger.warning("bilendi_id=%s completion failed: not in started state", bilendi_id)


def touch_activity(participant):
    bilendi_id = participant.vars.get("bilendi_id")
    if not bilendi_id:
        return
    from .models import BilendiRegistration
    BilendiRegistration.objects.filter(bilendi_id=bilendi_id).update(
        last_activity_at=timezone.now()
    )


def abandon_stale_registrations(timeout_seconds: int):
    from .models import BilendiRegistration
    threshold = timezone.now() - timezone.timedelta(seconds=timeout_seconds)
    count = BilendiRegistration.objects.filter(
        status="started", last_activity_at__lt=threshold
    ).update(status="abandoned")
    if count:
        logger.info("%d Bilendi registrations marked as abandoned", count)
    return count
