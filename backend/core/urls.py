"""URL routes for the core app — /api/config/"""
from django.urls import path
from .views import EnvConfigStatusView, EnvConfigUpdateView

urlpatterns = [
    path('status/', EnvConfigStatusView.as_view(), name='env-config-status'),
    path('update/', EnvConfigUpdateView.as_view(), name='env-config-update'),
]
