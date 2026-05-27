from django.urls import path
from .views import EntryView

urlpatterns = [
    path("", EntryView.as_view(), name="bilendi_entry"),
]
