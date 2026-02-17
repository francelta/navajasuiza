"""Admin management URL routes — /api/admin/"""
from django.urls import path
from .views import UserAdminListCreateView, UserAdminDetailView, EmployeeCreateView

urlpatterns = [
    path('users/', UserAdminListCreateView.as_view(), name='admin-users-list'),
    path('users/<int:pk>/', UserAdminDetailView.as_view(), name='admin-users-detail'),
    path('employees/', EmployeeCreateView.as_view(), name='admin-employees-create'),
]
