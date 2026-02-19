"""
Reports BI Serializers — Nested App Container pattern.
ReportApp nests its AppLoadScript[] and ReportSheet[].
"""
from rest_framework import serializers
from .models import DBConnection, ReportApp, AppLoadScript, ReportSheet


# ── DBConnection ──

class DBConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DBConnection
        fields = ['id', 'name', 'engine', 'host', 'port', 'database', 'username', 'password', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}


class DBConnectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DBConnection
        fields = ['id', 'name', 'engine', 'host', 'database']


# ── AppLoadScript ──

class AppLoadScriptSerializer(serializers.ModelSerializer):
    connection_name = serializers.CharField(source='connection.name', read_only=True)

    class Meta:
        model = AppLoadScript
        fields = [
            'id', 'app', 'connection', 'connection_name',
            'name', 'query_text', 'order',
            'last_row_count', 'last_executed_at', 'last_error',
        ]
        read_only_fields = ['id', 'last_row_count', 'last_executed_at', 'last_error']


# ── ReportSheet ──

class ReportSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSheet
        fields = ['id', 'app', 'title', 'layout_json', 'order']
        read_only_fields = ['id']


# ── ReportApp (nested) ──

class ReportAppDetailSerializer(serializers.ModelSerializer):
    """Full detail with nested scripts and sheets."""
    scripts = AppLoadScriptSerializer(many=True, read_only=True)
    sheets = ReportSheetSerializer(many=True, read_only=True)

    class Meta:
        model = ReportApp
        fields = ['id', 'name', 'description', 'scripts', 'sheets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportAppListSerializer(serializers.ModelSerializer):
    """Lightweight for the hub landing."""
    script_count = serializers.SerializerMethodField()
    sheet_count = serializers.SerializerMethodField()

    class Meta:
        model = ReportApp
        fields = ['id', 'name', 'description', 'script_count', 'sheet_count', 'created_at', 'updated_at']

    def get_script_count(self, obj):
        return obj.scripts.count()

    def get_sheet_count(self, obj):
        return obj.sheets.count()


class ReportAppCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportApp
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']
