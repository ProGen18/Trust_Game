"""
Configuration d'URL racine pour Trust-Game-AI.
Inclut les URLs oTree standard et les URLs Bilendi.
"""
from django.urls import include, path

import otree.urls
import config

urlpatterns = otree.urls.get_urlpatterns()

if config.BILENDI_ENABLED:
    urlpatterns.insert(0, path("bilendi/", include("bilendi.urls")))
