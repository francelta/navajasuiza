"""
Management command to create the initial SuperAdmin user.
Usage: python manage.py create_superadmin
"""
from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Crea el usuario SuperAdmin inicial para NavajaSuiza'

    def add_arguments(self, parser):
        parser.add_argument('--empleado-id', default='ADMIN001', help='ID del empleado (default: ADMIN001)')
        parser.add_argument('--username', default='superadmin', help='Username (default: superadmin)')
        parser.add_argument('--password', default='admin123', help='Password (default: admin123)')
        parser.add_argument('--email', default='admin@navajasuiza.local', help='Email')

    def handle(self, *args, **options):
        empleado_id = options['empleado_id']

        if CustomUser.objects.filter(empleado_id=empleado_id).exists():
            self.stdout.write(self.style.WARNING(
                f'El usuario con empleado_id "{empleado_id}" ya existe.'
            ))
            return

        user = CustomUser.objects.create_user(
            username=options['username'],
            email=options['email'],
            password=options['password'],
            empleado_id=empleado_id,
            role='superadmin',
            first_name='Super',
            last_name='Admin',
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f'✅ SuperAdmin creado exitosamente:\n'
            f'   Empleado ID: {user.empleado_id}\n'
            f'   Username:    {user.username}\n'
            f'   Password:    {options["password"]}\n'
            f'   Rol:         {user.role}'
        ))
