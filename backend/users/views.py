"""Views for the users app — Login, Profile, Admin CRUD, and Employee Management."""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import IsSuperAdmin
from core.email_service import send_welcome_email
from .models import CustomUser
from .serializers import (
    LoginSerializer,
    UserProfileSerializer,
    UserAdminSerializer,
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
)

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticates with empleado_id + password, returns JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    GET /api/users/me/
    Returns the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class UserAdminListCreateView(APIView):
    """
    GET  /api/admin/users/     — List all users (SuperAdmin only)
    POST /api/admin/users/     — Create a new user (SuperAdmin only)
    """
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserAdminSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserAdminDetailView(APIView):
    """
    GET    /api/admin/users/<id>/  — Get user details
    PATCH  /api/admin/users/<id>/  — Update user (including block/unblock)
    DELETE /api/admin/users/<id>/  — Deactivate user
    """
    permission_classes = [IsSuperAdmin]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {'detail': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserAdminSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {'detail': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserAdminSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {'detail': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.is_active = False
        user.save()
        return Response(
            {'detail': 'Usuario desactivado.'},
            status=status.HTTP_200_OK,
        )


# ============================================
# Employee CRUD (Sprint 4) — Full Management
# ============================================

class EmployeeListCreateView(APIView):
    """
    GET  /api/admin/employees/    — List all employees with readable passwords
    POST /api/admin/employees/    — Create employee + send welcome email
    """
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        employees = CustomUser.objects.filter(is_active=True).order_by('-date_joined')
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        plain_password = user._plain_password

        # Attempt to send the welcome email
        email_sent, error_msg = send_welcome_email(user, plain_password)

        if not email_sent:
            # Log the error but DON'T rollback — keep the user
            logger.warning(
                f'Email failed for {user.empleado_id}: {error_msg}. '
                f'User was created anyway.'
            )

        response_data = {
            'detail': (
                f'Empleado creado y email enviado a {user.email}.'
                if email_sent else
                f'Empleado creado pero el email NO se pudo enviar. '
                f'Comunica las credenciales manualmente.'
            ),
            'email_sent': email_sent,
            'user': EmployeeListSerializer(user).data,
        }

        if not email_sent:
            response_data['smtp_error'] = error_msg

        return Response(response_data, status=status.HTTP_201_CREATED)


class EmployeeDetailView(APIView):
    """
    PATCH  /api/admin/employees/<id>/  — Update employee
    DELETE /api/admin/employees/<id>/  — Delete employee
    """
    permission_classes = [IsSuperAdmin]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {'detail': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeUpdateSerializer(
            data=request.data,
            context={'instance': user},
        )
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.update(user, serializer.validated_data)

        return Response({
            'detail': 'Empleado actualizado correctamente.',
            'user': EmployeeListSerializer(updated_user).data,
        })

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {'detail': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        name = user.get_full_name() or user.empleado_id
        user.delete()

        return Response(
            {'detail': f'Empleado "{name}" eliminado permanentemente.'},
            status=status.HTTP_200_OK,
        )
