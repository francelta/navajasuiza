"""
Reports BI Views — App Container CRUD + Multi-Source Data Load.

DBConnection:   /api/reports/connections/              (GET, POST)
                /api/reports/connections/<id>/          (GET, PUT, DELETE)
                /api/reports/connections/<id>/test/     (POST)
ReportApp:      /api/reports/apps/                     (GET, POST)
                /api/reports/apps/<id>/                (GET, PUT, DELETE)
                /api/reports/apps/<id>/execute/         (POST — run all scripts)
AppLoadScript:  /api/reports/scripts/                   (POST create)
                /api/reports/scripts/<id>/              (GET, PUT, DELETE)
ReportSheet:    /api/reports/sheets/                    (POST create)
                /api/reports/sheets/<id>/               (GET, PUT, DELETE)
"""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import DBConnection, ReportApp, AppLoadScript, ReportSheet
from .serializers import (
    DBConnectionSerializer, DBConnectionListSerializer,
    ReportAppDetailSerializer, ReportAppListSerializer, ReportAppCreateSerializer,
    AppLoadScriptSerializer, ReportSheetSerializer,
)
from .services.query_engine import test_connection, execute_app_data_load

logger = logging.getLogger(__name__)


# ─── DBConnection ───

class DBConnectionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(DBConnectionListSerializer(DBConnection.objects.all(), many=True).data)

    def post(self, request):
        s = DBConnectionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(created_by=request.user)
        return Response(s.data, status=status.HTTP_201_CREATED)


class DBConnectionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            c = DBConnection.objects.get(pk=pk)
        except DBConnection.DoesNotExist:
            return Response({'detail': 'Conexión no encontrada.'}, status=404)
        return Response(DBConnectionSerializer(c).data)

    def put(self, request, pk):
        try:
            c = DBConnection.objects.get(pk=pk)
        except DBConnection.DoesNotExist:
            return Response({'detail': 'Conexión no encontrada.'}, status=404)
        s = DBConnectionSerializer(c, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        try:
            c = DBConnection.objects.get(pk=pk)
        except DBConnection.DoesNotExist:
            return Response({'detail': 'Conexión no encontrada.'}, status=404)
        c.delete()
        return Response({'detail': 'Conexión eliminada.'})


class DBConnectionTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            c = DBConnection.objects.get(pk=pk)
        except DBConnection.DoesNotExist:
            return Response({'detail': 'Conexión no encontrada.'}, status=404)
        ok, msg = test_connection(c)
        return Response({'success': ok, 'message': msg}, status=200 if ok else 422)


# ─── ReportApp ───

class ReportAppListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        apps = ReportApp.objects.prefetch_related('scripts', 'sheets').all()
        return Response(ReportAppListSerializer(apps, many=True).data)

    def post(self, request):
        s = ReportAppCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(created_by=request.user)
        return Response(s.data, status=status.HTTP_201_CREATED)


class ReportAppDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            app = ReportApp.objects.prefetch_related('scripts__connection', 'sheets').get(pk=pk)
        except ReportApp.DoesNotExist:
            return Response({'detail': 'App no encontrada.'}, status=404)
        return Response(ReportAppDetailSerializer(app).data)

    def put(self, request, pk):
        try:
            app = ReportApp.objects.get(pk=pk)
        except ReportApp.DoesNotExist:
            return Response({'detail': 'App no encontrada.'}, status=404)
        s = ReportAppCreateSerializer(app, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        try:
            app = ReportApp.objects.get(pk=pk)
        except ReportApp.DoesNotExist:
            return Response({'detail': 'App no encontrada.'}, status=404)
        app.delete()
        return Response({'detail': 'App eliminada.'})


class ReportAppExecuteView(APIView):
    """POST — Execute ALL load scripts of an app."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            result = execute_app_data_load(pk)
            logger.info(
                f'[BI] App {pk} loaded: {result["success_count"]}/{result["total_scripts"]} '
                f'scripts OK by {request.user.empleado_id}'
            )
            return Response(result)
        except ValueError as e:
            return Response({'detail': str(e)}, status=422)
        except Exception as e:
            logger.error(f'[BI] App execution error: {e}')
            return Response({'detail': str(e)}, status=500)


# ─── AppLoadScript ───

class AppLoadScriptCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = AppLoadScriptSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class AppLoadScriptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            sc = AppLoadScript.objects.select_related('connection').get(pk=pk)
        except AppLoadScript.DoesNotExist:
            return Response({'detail': 'Script no encontrado.'}, status=404)
        return Response(AppLoadScriptSerializer(sc).data)

    def put(self, request, pk):
        try:
            sc = AppLoadScript.objects.get(pk=pk)
        except AppLoadScript.DoesNotExist:
            return Response({'detail': 'Script no encontrado.'}, status=404)
        s = AppLoadScriptSerializer(sc, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        try:
            sc = AppLoadScript.objects.get(pk=pk)
        except AppLoadScript.DoesNotExist:
            return Response({'detail': 'Script no encontrado.'}, status=404)
        sc.delete()
        return Response({'detail': 'Script eliminado.'})


# ─── ReportSheet ───

class ReportSheetCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = ReportSheetSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_201_CREATED)


class ReportSheetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            sh = ReportSheet.objects.get(pk=pk)
        except ReportSheet.DoesNotExist:
            return Response({'detail': 'Hoja no encontrada.'}, status=404)
        return Response(ReportSheetSerializer(sh).data)

    def put(self, request, pk):
        try:
            sh = ReportSheet.objects.get(pk=pk)
        except ReportSheet.DoesNotExist:
            return Response({'detail': 'Hoja no encontrada.'}, status=404)
        s = ReportSheetSerializer(sh, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        try:
            sh = ReportSheet.objects.get(pk=pk)
        except ReportSheet.DoesNotExist:
            return Response({'detail': 'Hoja no encontrada.'}, status=404)
        sh.delete()
        return Response({'detail': 'Hoja eliminada.'})
