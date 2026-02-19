"""URL routes for reports — /api/reports/"""
from django.urls import path
from .views import ReportUploadView, ReportListView, ReportDataView, ReportDeleteView

urlpatterns = [
    path('', ReportListView.as_view(), name='reports-list'),
    path('upload/', ReportUploadView.as_view(), name='reports-upload'),
    path('<int:pk>/data/', ReportDataView.as_view(), name='reports-data'),
    path('<int:pk>/', ReportDeleteView.as_view(), name='reports-delete'),
]
