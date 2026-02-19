"""URL routes for reports BI — /api/reports/"""
from django.urls import path
from .views import (
    DBConnectionListCreateView, DBConnectionDetailView, DBConnectionTestView,
    ReportAppListCreateView, ReportAppDetailView, ReportAppExecuteView,
    AppLoadScriptCreateView, AppLoadScriptDetailView,
    ReportSheetCreateView, ReportSheetDetailView,
)

urlpatterns = [
    # DB Connections (global)
    path('connections/', DBConnectionListCreateView.as_view()),
    path('connections/<int:pk>/', DBConnectionDetailView.as_view()),
    path('connections/<int:pk>/test/', DBConnectionTestView.as_view()),

    # Report Apps
    path('apps/', ReportAppListCreateView.as_view()),
    path('apps/<int:pk>/', ReportAppDetailView.as_view()),
    path('apps/<int:pk>/execute/', ReportAppExecuteView.as_view()),

    # Load Scripts (belong to an app)
    path('scripts/', AppLoadScriptCreateView.as_view()),
    path('scripts/<int:pk>/', AppLoadScriptDetailView.as_view()),

    # Sheets (belong to an app)
    path('sheets/', ReportSheetCreateView.as_view()),
    path('sheets/<int:pk>/', ReportSheetDetailView.as_view()),
]
