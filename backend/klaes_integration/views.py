"""
Views for the Klaes SQL Server Integration.
Translated from FastAPI to Django REST Framework.

FastAPI Depends(verify_token) → DRF IsAuthenticated
FastAPI @app.get → DRF APIView.get
FastAPI @app.put → DRF APIView.put
"""
import logging
from decimal import Decimal, InvalidOperation

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .db import get_material_info, update_material_price, get_quotation_details

logger = logging.getLogger(__name__)


class KlaesMaterialView(APIView):
    """
    GET /api/klaes/material/<material_id>/
    Query material data from the Klaes SQL Server database.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, material_id):
        if not material_id or not material_id.strip():
            return Response(
                {'detail': 'El ID de material es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        material_id = material_id.strip()

        # Log who queried
        logger.info(
            f'[KLAES] Material query: "{material_id}" '
            f'by {request.user.empleado_id}'
        )

        try:
            data = get_material_info(material_id)
        except RuntimeError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            logger.error(f'[KLAES] Query error: {e}')
            return Response(
                {'detail': f'Error al consultar Klaes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if data is None:
            return Response(
                {'detail': f'Material "{material_id}" no encontrado en Klaes.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            'material': data,
            'queried_by': request.user.empleado_id,
        })


class KlaesPriceUpdateView(APIView):
    """
    PUT /api/klaes/price/
    Update the sale price for a material in Klaes.
    Body: { "material_id": "...", "new_price": 99.50 }
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        material_id = request.data.get('material_id', '').strip()
        raw_price = request.data.get('new_price')

        if not material_id:
            return Response(
                {'detail': 'El campo "material_id" es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if raw_price is None:
            return Response(
                {'detail': 'El campo "new_price" es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate price
        try:
            new_price = Decimal(str(raw_price))
            if new_price < 0:
                raise ValueError('negative')
        except (InvalidOperation, ValueError, TypeError):
            return Response(
                {'detail': 'El precio debe ser un número positivo válido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Audit: log who updated with their empleado_id
        updated_by = f'API_NAVAJASUIZA_{request.user.empleado_id}'

        logger.info(
            f'[KLAES] Price update request: {material_id} → {new_price} '
            f'by {updated_by}'
        )

        try:
            success, message = update_material_price(
                material_id=material_id,
                new_price=float(new_price),
                updated_by=updated_by,
            )
        except RuntimeError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            logger.error(f'[KLAES] Update error: {e}')
            return Response(
                {'detail': f'Error al actualizar en Klaes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if success:
            return Response({
                'detail': message,
                'material_id': material_id,
                'new_price': float(new_price),
                'updated_by': updated_by,
            })
        else:
            return Response(
                {'detail': message},
                status=status.HTTP_404_NOT_FOUND,
            )


class KlaesQuotationDetailView(APIView):
    """
    GET /api/klaes/quotation/<q_number>/
    Busca un presupuesto por su número (ej: Q230001).
    Devuelve cabecera (cliente, estado, fecha, total) + líneas de ítems.
    Translated from FastAPI: @app.get("/v1/quotation/{q_number}")
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, q_number):
        if not q_number or not q_number.strip():
            return Response(
                {'detail': 'El número de presupuesto es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        q_number = q_number.strip()

        logger.info(
            f'[KLAES] Quotation query: "{q_number}" '
            f'by {request.user.empleado_id}'
        )

        try:
            data, error = get_quotation_details(q_number)
        except RuntimeError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            logger.error(f'[KLAES] Quotation error: {e}')
            return Response(
                {'detail': f'Error en servidor Klaes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if data is None:
            return Response(
                {'detail': error},
                status=status.HTTP_404_NOT_FOUND,
            )

        data['queried_by'] = request.user.empleado_id
        return Response(data)
