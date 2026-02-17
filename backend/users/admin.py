"""Django admin configuration for CustomUser."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('empleado_id', 'username', 'email', 'role', 'departamento', 'is_blocked', 'is_active')
    list_filter = ('role', 'is_blocked', 'is_active', 'departamento')
    search_fields = ('empleado_id', 'username', 'email', 'first_name', 'last_name')
    ordering = ('empleado_id',)

    fieldsets = UserAdmin.fieldsets + (
        ('Datos Empresariales', {
            'fields': ('empleado_id', 'role', 'departamento', 'is_blocked'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos Empresariales', {
            'fields': ('empleado_id', 'role', 'departamento'),
        }),
    )
