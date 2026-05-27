"""
Lanceur du serveur oTree avec route Bilendi injectée.

Utilisation:
    python runserver.py              # port 8000 par défaut
    python runserver.py 8005         # port custom

Remplace `otree devserver` quand BILENDI_ENABLED=True.
"""
import os
import sys

os.environ.setdefault("OTREE_PRODUCTION", "0")

# Charge l'app oTree (déclenche tous les imports et la construction de Starlette)
from otree.asgi import app

# Injecte la route Bilendi dans le router déjà construit
import config

if config.BILENDI_ENABLED:
    from starlette.routing import Route
    from bilendi.otree_views import BilendiEntry

    if not any(getattr(r, "path", None) == "/bilendi/" for r in app.router.routes):
        app.router.routes.insert(0, Route("/bilendi/", BilendiEntry))
        print(">>> Route /bilendi/ injectée")


if __name__ == "__main__":
    import uvicorn

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f">>> Serveur sur http://localhost:{port}")
    print(">>> Ctrl+C pour quitter\n")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        ws="websockets",
        log_level="warning",
    )
