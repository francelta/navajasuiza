"""Custom permissions for NavajaSuiza."""
from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Only allows access to SuperAdmin users."""
    message = 'Acceso restringido a SuperAdmin.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'is_superadmin')
            and request.user.is_superadmin
        )


class IsAdminUser(BasePermission):
    """Allows access to SuperAdmin and Admin users."""
    message = 'Acceso restringido a administradores.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'is_admin_user')
            and request.user.is_admin_user
        )
