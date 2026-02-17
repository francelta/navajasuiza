"""API views for the tools app."""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .klaes_service import run_pipeline

logger = logging.getLogger(__name__)


class KlaesReprocessView(APIView):
    """
    POST /api/tools/klaes/reprocess/
    Runs the full Klaes XML reprocessing pipeline.

    Input: { "code": "Q1234567" }
    Output: { "success": true/false, "steps": [...], "summary": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '').strip()

        if not code:
            return Response(
                {'detail': 'El campo "code" es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            f'Klaes reprocess initiated by {request.user.empleado_id} '
            f'for code: {code}'
        )

        # Run the full pipeline
        step_results = run_pipeline(code)

        # Build response
        steps_data = [step.to_dict() for step in step_results]
        all_ok = all(s.status in ('ok', 'warning') for s in step_results)
        last_step = step_results[-1] if step_results else None

        if all_ok:
            summary = f'✅ Reprocesamiento de {code.upper()} completado con éxito.'
            http_status = status.HTTP_200_OK
        else:
            summary = f'❌ Error en paso {last_step.step}: {last_step.message}'
            http_status = status.HTTP_422_UNPROCESSABLE_ENTITY

        return Response(
            {
                'success': all_ok,
                'code': code.upper(),
                'steps': steps_data,
                'summary': summary,
            },
            status=http_status,
        )
