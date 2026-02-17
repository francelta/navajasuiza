"""Views for the core app — system configuration."""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.permissions import IsSuperAdmin
from core.env_config_service import get_env_status, update_env_var


class EnvConfigStatusView(APIView):
    """
    GET /api/config/status/
    Returns the status of all required .env variables.
    Grouped by category, with is_set flag.
    [AGENTE_SEGURIDAD] Sensitive values never exposed.
    """
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        variables = get_env_status()

        # Group by category for the frontend
        groups = {}
        for var in variables:
            group = var['group']
            if group not in groups:
                groups[group] = {
                    'name': group,
                    'variables': [],
                    'configured': 0,
                    'total': 0,
                }
            groups[group]['variables'].append(var)
            groups[group]['total'] += 1
            if var['is_set']:
                groups[group]['configured'] += 1

        total_set = sum(1 for v in variables if v['is_set'])
        total_vars = len(variables)

        return Response({
            'groups': list(groups.values()),
            'summary': {
                'total': total_vars,
                'configured': total_set,
                'pending': total_vars - total_set,
                'percentage': round((total_set / total_vars * 100) if total_vars else 0),
            },
        })


class EnvConfigUpdateView(APIView):
    """
    POST /api/config/update/
    Updates a single .env variable.
    Input: { "key": "EMAIL_HOST", "value": "mail.example.com" }
    Rejects if the variable already has a real value.
    """
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        key = request.data.get('key', '').strip()
        value = request.data.get('value', '').strip()

        if not key:
            return Response(
                {'detail': 'El campo "key" es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not value:
            return Response(
                {'detail': 'El campo "value" es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = update_env_var(key, value)

        if success:
            return Response({'detail': message})
        else:
            return Response(
                {'detail': message},
                status=status.HTTP_409_CONFLICT,
            )
