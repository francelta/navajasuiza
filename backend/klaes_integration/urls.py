"""URL routes for klaes_integration — /api/klaes/"""
from django.urls import path
from .views import KlaesMaterialView, KlaesPriceUpdateView

urlpatterns = [
    path('material/<str:material_id>/', KlaesMaterialView.as_view(), name='klaes-material'),
    path('price/', KlaesPriceUpdateView.as_view(), name='klaes-price-update'),
]
