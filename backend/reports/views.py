"""
Reports API Views — File upload and data retrieval.

POST /api/reports/upload/     Upload a data file (CSV, XLSX, QVD)
GET  /api/reports/            List all uploaded reports
GET  /api/reports/<id>/data/  Get processed chart data
DELETE /api/reports/<id>/     Delete a report
"""
import logging
from datetime import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ReportFile
from .services.qlik_parser import process_file

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'qvd'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class ReportUploadView(APIView):
    """
    POST /api/reports/upload/
    Upload and process a data file.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'detail': 'No se ha enviado ningún archivo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate extension
        filename = uploaded_file.name
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {'detail': f'Formato no soportado: ".{ext}". Acepta: {", ".join(ALLOWED_EXTENSIONS)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate size
        if uploaded_file.size > MAX_FILE_SIZE:
            return Response(
                {'detail': f'Archivo demasiado grande ({uploaded_file.size // 1024 // 1024}MB). Máximo: {MAX_FILE_SIZE // 1024 // 1024}MB.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the record
        report = ReportFile.objects.create(
            file=uploaded_file,
            original_filename=filename,
            file_type=ext,
            file_size=uploaded_file.size,
            uploaded_by=request.user,
            status=ReportFile.Status.PROCESSING,
        )

        # Process the file
        try:
            filepath = report.file.path
            processed, row_count, col_count, columns = process_file(filepath)

            report.processed_data = processed
            report.row_count = row_count
            report.column_count = col_count
            report.columns_detected = columns
            report.status = ReportFile.Status.COMPLETED
            report.processed_at = datetime.now()
            report.save()

            logger.info(
                f'[REPORTS] File processed: {filename} '
                f'({row_count} rows × {col_count} cols) '
                f'by {request.user.empleado_id}'
            )

            return Response({
                'id': report.id,
                'filename': filename,
                'status': report.status,
                'row_count': row_count,
                'column_count': col_count,
                'charts_generated': len(processed.get('charts', [])),
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            report.status = ReportFile.Status.ERROR
            report.error_message = str(e)
            report.save()

            logger.error(f'[REPORTS] Processing error for {filename}: {e}')
            return Response(
                {'detail': f'Error al procesar archivo: {str(e)}'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )


class ReportListView(APIView):
    """
    GET /api/reports/
    List all uploaded reports for the current user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = ReportFile.objects.all().order_by('-uploaded_at')
        data = [{
            'id': r.id,
            'filename': r.original_filename,
            'file_type': r.file_type,
            'file_size': r.file_size,
            'status': r.status,
            'uploaded_by': r.uploaded_by.empleado_id,
            'uploaded_at': r.uploaded_at.isoformat(),
            'row_count': r.row_count,
            'column_count': r.column_count,
            'charts_count': len(r.processed_data.get('charts', [])) if r.processed_data else 0,
        } for r in reports]

        return Response(data)


class ReportDataView(APIView):
    """
    GET /api/reports/<id>/data/
    Return the processed chart data for a report.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            report = ReportFile.objects.get(pk=pk)
        except ReportFile.DoesNotExist:
            return Response(
                {'detail': 'Informe no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.status != ReportFile.Status.COMPLETED:
            return Response(
                {'detail': f'Informe en estado "{report.get_status_display()}". No hay datos disponibles.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'id': report.id,
            'filename': report.original_filename,
            'row_count': report.row_count,
            'column_count': report.column_count,
            'processed_at': report.processed_at.isoformat() if report.processed_at else None,
            **report.processed_data,
        })


class ReportDeleteView(APIView):
    """
    DELETE /api/reports/<id>/
    Delete a report and its file.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            report = ReportFile.objects.get(pk=pk)
        except ReportFile.DoesNotExist:
            return Response(
                {'detail': 'Informe no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        filename = report.original_filename

        # Delete the file from disk
        if report.file:
            try:
                report.file.delete(save=False)
            except Exception:
                pass

        report.delete()

        logger.info(f'[REPORTS] Deleted: {filename} by {request.user.empleado_id}')
        return Response(
            {'detail': f'Informe "{filename}" eliminado.'},
            status=status.HTTP_200_OK,
        )
