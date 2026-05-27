import csv
import io
import logging

from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from django.utils import timezone

from .models import BilendiRegistration

logger = logging.getLogger("bilendi")


@admin.register(BilendiRegistration)
class BilendiRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "bilendi_id", "status", "participant_code",
        "computed_gain", "adjusted_gain",
        "created_at", "completed_at", "exported_at",
    ]
    list_editable = ["adjusted_gain"]
    list_filter = ["status", "exported_at"]
    search_fields = ["bilendi_id", "participant_code"]
    actions = ["reset_to_imported", "mark_as_exported", "export_csv"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-whitelist/",
                self.admin_site.admin_view(self.import_whitelist_view),
                name="bilendi_import_whitelist",
            ),
        ]
        return custom_urls + urls

    # --- Actions ---

    @admin.action(description="Réinitialiser en 'importé' (permet de renvoyer l'invitation)")
    def reset_to_imported(self, request, queryset):
        updated = queryset.filter(status__in=["started", "abandoned"]).update(
            status="imported", participant_code=""
        )
        self.message_user(request, f"{updated} inscription(s) réinitialisée(s).")

    @admin.action(description="Marquer comme exporté")
    def mark_as_exported(self, request, queryset):
        updated = queryset.filter(exported_at__isnull=True).update(
            exported_at=timezone.now()
        )
        self.message_user(request, f"{updated} inscription(s) marquée(s) comme exportée(s).")

    @admin.action(description="Exporter CSV pour Bilendi")
    def export_csv(self, request, queryset):
        qs = queryset.filter(status="completed", exported_at__isnull=True)
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        writer.writerow(["bilendi_id", "computed_gain", "adjusted_gain", "completed_at"])

        for reg in qs:
            writer.writerow([
                reg.bilendi_id,
                str(reg.computed_gain) if reg.computed_gain is not None else "",
                str(reg.adjusted_gain) if reg.adjusted_gain is not None else "",
                reg.completed_at.isoformat() if reg.completed_at else "",
            ])

        response = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="bilendi_export.csv"'
        return response

    # --- Vue custom : import whitelist ---

    def import_whitelist_view(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("whitelist_csv")
            if not csv_file:
                self.message_user(request, "Aucun fichier CSV fourni.", level=messages.ERROR)
                return redirect("..")

            try:
                text = csv_file.read().decode("utf-8-sig")
            except UnicodeDecodeError:
                try:
                    csv_file.seek(0)
                    text = csv_file.read().decode("latin-1")
                except Exception:
                    self.message_user(
                        request, "Encoding non supporté (UTF-8 ou Latin-1 attendu).",
                        level=messages.ERROR,
                    )
                    return redirect("..")

            reader = csv.reader(io.StringIO(text), delimiter=";")
            # fallback virgule si le séparateur point-virgule ne donne qu'une colonne
            first_row = next(reader, None)
            if first_row is None:
                self.message_user(request, "CSV vide.", level=messages.ERROR)
                return redirect("..")
            if len(first_row) == 1 and "," in first_row[0]:
                csv_file.seek(0)
                text = csv_file.read().decode("utf-8-sig")
                reader = csv.reader(io.StringIO(text), delimiter=",")
                first_row = next(reader, None)

            # Détecter le header ou non
            if first_row and first_row[0].strip().lower() in ("bilendi_id", "id", "bilendiid"):
                pass  # c'est un header, on commence déjà à la 2e ligne
            else:
                reader = iter([first_row] + list(reader))

            created, skipped, errors = 0, 0, 0
            for row in reader:
                if not row or not row[0].strip():
                    continue
                bilendi_id = row[0].strip()
                if not bilendi_id:
                    errors += 1
                    continue
                _, was_created = BilendiRegistration.objects.get_or_create(
                    bilendi_id=bilendi_id,
                    defaults={"status": "imported"},
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

            self.message_user(
                request,
                f"Import terminé : {created} créé(s), {skipped} ignoré(s) (doublons), {errors} erreur(s).",
            )
            logger.info(
                "bilendi whitelist imported: created=%d skipped=%d errors=%d",
                created, skipped, errors,
            )
            return redirect("..")

        return render(request, "admin/bilendi_import.html")
