"""URL routes for the tools app — /api/tools/"""
from django.urls import path
from .views import KlaesReprocessView

urlpatterns = [
    path('klaes/reprocess/', KlaesReprocessView.as_view(), name='klaes-reprocess'),
]
