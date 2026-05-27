"""
Wrapper ASGI pour oTree + Bilendi.

Ce module est la cible d'uvicorn (configurée dans le Procfile).
Il charge l'app oTree standard, puis y injecte les routes Bilendi
si BILENDI_ENABLED=True.

Aucune modification de oTree n'est nécessaire — on se contente d'ajouter
nos routes au router Starlette de l'app après sa construction.
"""
import logging

from otree.asgi import app  # déclenche la construction complète de l'app oTree

import config

logger = logging.getLogger("bilendi")


def _inject_bilendi_routes():
    if not config.BILENDI_ENABLED:
        return

    from starlette.routing import Route
    from bilendi.otree_views import BilendiEntry, BilendiExport

    routes_to_add = [
        Route("/bilendi/", BilendiEntry, name="bilendi_entry"),
        Route("/bilendi/export", BilendiExport, name="bilendi_export"),
    ]

    existing_paths = {getattr(r, "path", None) for r in app.router.routes}
    for route in routes_to_add:
        if route.path not in existing_paths:
            app.router.routes.insert(0, route)
            logger.info("Route %s injectée", route.path)
            print(f">>> Route {route.path} injectée")


_inject_bilendi_routes()
