"""Admin management URL routes — /api/admin/"""
from django.urls import path
from .views import (
    UserAdminListCreateView,
    UserAdminDetailView,
    EmployeeListCreateView,
    EmployeeDetailView,
)

urlpatterns = [
    path('users/', UserAdminListCreateView.as_view(), name='admin-users-list'),
    path('users/<int:pk>/', UserAdminDetailView.as_view(), name='admin-users-detail'),
    path('employees/', EmployeeListCreateView.as_view(), name='admin-employees-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='admin-employees-detail'),
]
