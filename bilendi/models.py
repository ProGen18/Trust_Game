from django.db import models


class BilendiRegistration(models.Model):
    bilendi_id = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(
        max_length=16, default="imported", db_index=True,
        choices=[
            ("imported", "Importé"),
            ("started", "Commencé"),
            ("abandoned", "Abandonné"),
            ("completed", "Complété"),
        ],
    )
    participant_code = models.CharField(max_length=64, blank=True, db_index=True)
    computed_gain = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    adjusted_gain = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trust_game_skipped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    exported_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "exported_at"]),
        ]

    def __str__(self):
        return f"Bilendi {self.bilendi_id} ({self.status})"
