from django.apps import AppConfig


class BilendiConfig(AppConfig):
    name = "bilendi"
    verbose_name = "Intégration Bilendi"

    def ready(self):
        from django.conf import settings
        if not getattr(settings, "BILENDI_ENABLED", False):
            return

        mw = "bilendi.middleware.BilendiValidationMiddleware"
        if mw not in settings.MIDDLEWARE:
            for i, m in enumerate(settings.MIDDLEWARE):
                if m.endswith("SessionMiddleware"):
                    settings.MIDDLEWARE.insert(i + 1, mw)
                    break
