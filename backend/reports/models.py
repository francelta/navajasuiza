"""
Reports BI Models — Application Container Architecture.

DBConnection:    Global reusable database connections
ReportApp:       The BI application container (≈ Qlik .qvf)
AppLoadScript:   N load scripts per app, each hitting a different DB
ReportSheet:     N visualization sheets per app
"""
from django.conf import settings
from django.db import models


class DBConnection(models.Model):
    """Global repository of reusable database connections."""

    ENGINE_CHOICES = [
        ('sqlserver', 'SQL Server'),
        ('mysql', 'MySQL'),
        ('postgresql', 'PostgreSQL'),
    ]

    name = models.CharField(max_length=100, unique=True)
    engine = models.CharField(max_length=50, choices=ENGINE_CHOICES, default='sqlserver')
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=1433)
    database = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='db_connections',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.engine}://{self.host}/{self.database})'


class ReportApp(models.Model):
    """
    The BI Application Container — equivalent to a Qlik .qvf file.
    Contains N load scripts and N visualization sheets.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='report_apps',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class AppLoadScript(models.Model):
    """
    A load script tab inside a ReportApp.
    Each script connects to a specific DB and runs a SQL query.
    Multiple scripts form a multi-source data model.
    """
    app = models.ForeignKey(
        ReportApp, on_delete=models.CASCADE, related_name='scripts',
    )
    connection = models.ForeignKey(
        DBConnection, on_delete=models.RESTRICT, related_name='load_scripts',
    )
    name = models.CharField(max_length=100, help_text='Ej: Extracción Clientes Sage')
    query_text = models.TextField(help_text='SELECT query to execute')
    order = models.IntegerField(default=0, help_text='Execution order')

    # Cached execution metadata
    last_row_count = models.PositiveIntegerField(default=0)
    last_executed_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.name} → {self.connection.name}'


class ReportSheet(models.Model):
    """
    A visualization sheet inside a ReportApp.
    layout_json stores chart configurations referencing data from load scripts.
    [
        {"id": "c_1", "type": "bar", "title": "Ventas",
         "source": "script_name", "dimension": "Region", "metric": "Total"}
    ]
    """
    app = models.ForeignKey(
        ReportApp, on_delete=models.CASCADE, related_name='sheets',
    )
    title = models.CharField(max_length=255)
    layout_json = models.JSONField(default=list)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.title} (App: {self.app.name})'
