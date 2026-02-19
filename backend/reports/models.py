"""
ReportFile model — stores uploaded data files for dashboard generation.
"""
from django.conf import settings
from django.db import models


class ReportFile(models.Model):
    """An uploaded data file (QVD, CSV, XLSX) for processing into dashboards."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PROCESSING = 'processing', 'Procesando'
        COMPLETED = 'completed', 'Completado'
        ERROR = 'error', 'Error'

    file = models.FileField(
        upload_to='reports/%Y/%m/',
        help_text='Archivo de datos (QVD, CSV, XLSX)',
    )
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(
        max_length=10,
        help_text='Extensión del archivo (csv, qvd, xlsx)',
    )
    file_size = models.PositiveIntegerField(
        default=0,
        help_text='Tamaño en bytes',
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_reports',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error_message = models.TextField(blank=True, default='')

    # Processed data stored as JSON (ready for Chart.js)
    processed_data = models.JSONField(
        null=True,
        blank=True,
        help_text='JSON procesado listo para Chart.js',
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    row_count = models.PositiveIntegerField(default=0)
    column_count = models.PositiveIntegerField(default=0)
    columns_detected = models.JSONField(
        null=True,
        blank=True,
        help_text='Lista de columnas detectadas con tipo',
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Archivo de Informe'
        verbose_name_plural = 'Archivos de Informes'

    def __str__(self):
        return f'{self.original_filename} ({self.status})'
