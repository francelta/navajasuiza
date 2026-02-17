"""
CustomUser model for NavajaSuiza enterprise system.
Extends Django's AbstractUser with role-based access, employee ID, and blocking.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Enterprise user model.
    - No public registration: only SuperAdmin creates accounts.
    - Identified by empleado_id (employee ID) for login.
    - Supports blocking/deactivating users.
    """

    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', 'SuperAdmin'
        ADMIN = 'admin', 'Administrador'
        EMPLEADO = 'empleado', 'Empleado'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLEADO,
        verbose_name='Rol',
    )
    empleado_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='ID Empleado',
        help_text='Identificador único del empleado (ej: EMP001)',
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Departamento',
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name='Bloqueado',
        help_text='Si está activo, el usuario no puede iniciar sesión.',
    )

    # Use empleado_id as the login field
    USERNAME_FIELD = 'empleado_id'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['empleado_id']

    def __str__(self):
        return f'{self.empleado_id} - {self.get_full_name() or self.username}'

    @property
    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN

    @property
    def is_admin_user(self):
        return self.role in (self.Role.SUPERADMIN, self.Role.ADMIN)
