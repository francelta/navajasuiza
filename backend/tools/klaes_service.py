"""
KlaesReprocessingService — Core business logic for Klaes XML reprocessing.

Pipeline:
  1. Validate production code (Q/R + 7 digits)
  2. Search XML in 3 sequential paths
  3. Copy XML to import folder
  4. Execute external ETL
  5. Backup generated CSV
  6. Send to Sage X3 via Web Service
"""
import os
import re
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# Regex: Q or R followed by exactly 7 digits
CODE_PATTERN = re.compile(r'^[QR]\d{7}$')


class KlaesStepResult:
    """Represents the result of a single pipeline step."""

    def __init__(self, step, status, message, detail=None):
        self.step = step          # Step number (1-6)
        self.status = status      # 'ok', 'error', 'warning', 'pending'
        self.message = message    # Human-readable message
        self.detail = detail      # Optional extra info

    def to_dict(self):
        d = {
            'step': self.step,
            'status': self.status,
            'message': self.message,
        }
        if self.detail:
            d['detail'] = self.detail
        return d


def _sanitize_path(base_path, filename):
    """
    [AGENTE_SEGURIDAD] Prevent path traversal attacks.
    Ensures the resolved file path stays within the base directory.
    """
    base = Path(base_path).resolve()
    target = (base / filename).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError(
            f'Path traversal detectado: "{filename}" intenta salir de "{base}"'
        )
    return target


def validate_code(code):
    """
    Step 1: Validate production code format.
    Must be Q or R + 7 digits (e.g., Q1234567, R9876543).
    """
    if not code or not CODE_PATTERN.match(code.upper()):
        return KlaesStepResult(
            step=1,
            status='error',
            message=f'Código inválido: "{code}". Formato esperado: Q/R + 7 dígitos.',
        )

    return KlaesStepResult(
        step=1,
        status='ok',
        message=f'Código "{code.upper()}" validado correctamente.',
    )


def search_xml(code):
    """
    Step 2: Search for {CODE}.xml in 3 configured paths sequentially.
    Returns the path where found, or error if not found.
    """
    filename = f'{code.upper()}.xml'
    search_paths = settings.KLAES_SEARCH_PATHS

    for i, search_path in enumerate(search_paths, 1):
        if not search_path:
            continue

        try:
            full_path = _sanitize_path(search_path, filename)
            if full_path.exists():
                return KlaesStepResult(
                    step=2,
                    status='ok',
                    message=f'Archivo encontrado en Ruta {i}: {search_path}',
                    detail={'found_path': str(full_path), 'route_number': i},
                )
        except ValueError as e:
            logger.warning(f'Path traversal attempt: {e}')
            return KlaesStepResult(
                step=2,
                status='error',
                message='Código inválido: posible intento de acceso no autorizado.',
            )

    # Not found in any path
    searched = [p for p in search_paths if p]
    return KlaesStepResult(
        step=2,
        status='error',
        message='El archivo no se encuentra en las carpetas configuradas.',
        detail={'searched_paths': searched, 'filename': filename},
    )


def copy_to_import(source_path, code):
    """
    Step 3: Copy the XML file to the import folder.
    """
    import_dir = settings.KLAES_IMPORT_PATH
    if not import_dir:
        return KlaesStepResult(
            step=3,
            status='error',
            message='Carpeta de importación no configurada (PATH_IMPORTACION_QR).',
        )

    filename = f'{code.upper()}.xml'

    try:
        dest_path = _sanitize_path(import_dir, filename)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(source_path, dest_path)

        return KlaesStepResult(
            step=3,
            status='ok',
            message=f'Archivo copiado a carpeta de importación.',
            detail={'destination': str(dest_path)},
        )
    except Exception as e:
        return KlaesStepResult(
            step=3,
            status='error',
            message=f'Error al copiar archivo: {str(e)}',
        )


def execute_etl():
    """
    Step 4: Execute the external ETL command (Klaes → Sage format).
    """
    etl_cmd = settings.KLAES_ETL_COMMAND
    if not etl_cmd:
        return KlaesStepResult(
            step=4,
            status='error',
            message='Comando ETL no configurado (CMD_ETL_KLAES_SAGE).',
        )

    try:
        result = subprocess.run(
            etl_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
        )

        if result.returncode == 0:
            return KlaesStepResult(
                step=4,
                status='ok',
                message='ETL ejecutado correctamente.',
                detail={'stdout': result.stdout[:500] if result.stdout else None},
            )
        else:
            return KlaesStepResult(
                step=4,
                status='error',
                message=f'ETL falló con código de salida {result.returncode}.',
                detail={'stderr': result.stderr[:500] if result.stderr else None},
            )

    except subprocess.TimeoutExpired:
        return KlaesStepResult(
            step=4,
            status='error',
            message='ETL excedió el tiempo límite (120s).',
        )
    except FileNotFoundError:
        return KlaesStepResult(
            step=4,
            status='error',
            message=f'Comando ETL no encontrado: "{etl_cmd}".',
        )
    except Exception as e:
        return KlaesStepResult(
            step=4,
            status='error',
            message=f'Error inesperado al ejecutar ETL: {str(e)}',
        )


def backup_csv():
    """
    Step 5: Create a timestamped backup of the CSV generated by the ETL.
    The CSV is in PATH_OUTPUT_CSV. Backup name: importacioncsv_{YYYYMMDD_HHMMSS}.csv
    """
    csv_dir = settings.KLAES_CSV_OUTPUT_PATH
    if not csv_dir:
        return KlaesStepResult(
            step=5,
            status='error',
            message='Ruta de salida CSV no configurada (PATH_OUTPUT_CSV).',
        )

    csv_path = Path(csv_dir)
    if not csv_path.exists():
        return KlaesStepResult(
            step=5,
            status='error',
            message=f'La carpeta CSV no existe: {csv_dir}',
        )

    # Find the most recent CSV file in the output folder
    csv_files = sorted(csv_path.glob('*.csv'), key=os.path.getmtime, reverse=True)
    if not csv_files:
        return KlaesStepResult(
            step=5,
            status='warning',
            message='No se encontró ningún CSV en la carpeta de salida.',
        )

    source_csv = csv_files[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'importacioncsv_{timestamp}.csv'

    try:
        backup_path = source_csv.parent / backup_name
        shutil.copy2(source_csv, backup_path)

        return KlaesStepResult(
            step=5,
            status='ok',
            message=f'Backup CSV creado: {backup_name}',
            detail={'backup_path': str(backup_path), 'original': str(source_csv)},
        )
    except Exception as e:
        return KlaesStepResult(
            step=5,
            status='error',
            message=f'Error al hacer backup del CSV: {str(e)}',
        )


def send_to_sage(csv_path=None):
    """
    Step 6: Import data into Sage X3 via Web Service (SOAP).
    Uses the KLAES import template configured in settings.
    """
    ws_url = settings.SAGE_WS_URL
    ws_user = settings.SAGE_WS_USER
    ws_password = settings.SAGE_WS_PASSWORD
    pool_alias = settings.SAGE_POOL_ALIAS
    language = settings.SAGE_WS_LANGUAGE
    template = settings.SAGE_WS_IMPORT_TEMPLATE

    if not ws_url:
        return KlaesStepResult(
            step=6,
            status='error',
            message='Sage Web Service URL no configurada (SAGE_WS_URL).',
        )

    # Build SOAP envelope for Sage X3 import
    soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:wss="http://www.adonix.com/WSS">
    <soapenv:Header/>
    <soapenv:Body>
        <wss:run>
            <callContext>
                <codeLang>{language}</codeLang>
                <poolAlias>{pool_alias}</poolAlias>
                <requestConfig>adxwss.optreturn=JSON</requestConfig>
            </callContext>
            <publicName>{template}</publicName>
        </wss:run>
    </soapenv:Body>
</soapenv:Envelope>"""

    try:
        import requests
        from requests.auth import HTTPBasicAuth

        response = requests.post(
            ws_url,
            data=soap_body,
            headers={'Content-Type': 'text/xml; charset=utf-8'},
            auth=HTTPBasicAuth(ws_user, ws_password),
            timeout=60,
            verify=False,  # Internal network — self-signed certs common
        )

        if response.status_code == 200:
            # Check for SOAP fault in response
            if '<faultcode>' in response.text:
                fault_msg = response.text[:300]
                return KlaesStepResult(
                    step=6,
                    status='error',
                    message='Sage X3 devolvió un error SOAP.',
                    detail={'soap_fault': fault_msg},
                )

            return KlaesStepResult(
                step=6,
                status='ok',
                message='Datos importados en Sage X3 correctamente.',
                detail={'http_status': response.status_code},
            )
        else:
            return KlaesStepResult(
                step=6,
                status='error',
                message=f'Sage X3 respondió con HTTP {response.status_code}.',
                detail={'response_body': response.text[:300]},
            )

    except requests.exceptions.ConnectionError:
        return KlaesStepResult(
            step=6,
            status='error',
            message='No se pudo conectar con Sage X3. Verifica SAGE_WS_URL.',
        )
    except requests.exceptions.Timeout:
        return KlaesStepResult(
            step=6,
            status='error',
            message='Conexión con Sage X3 excedió el tiempo límite (60s).',
        )
    except ImportError:
        return KlaesStepResult(
            step=6,
            status='error',
            message='Módulo "requests" no instalado. Ejecuta: pip install requests',
        )
    except Exception as e:
        return KlaesStepResult(
            step=6,
            status='error',
            message=f'Error inesperado con Sage X3: {str(e)}',
        )


def run_pipeline(code):
    """
    Execute the full Klaes reprocessing pipeline.
    Returns a list of step results. Stops on critical errors.
    """
    steps = []

    # Step 1: Validate code
    step1 = validate_code(code)
    steps.append(step1)
    if step1.status == 'error':
        return steps

    code = code.upper()

    # Step 2: Search XML
    step2 = search_xml(code)
    steps.append(step2)
    if step2.status == 'error':
        return steps

    found_path = step2.detail['found_path']

    # Step 3: Copy to import folder
    step3 = copy_to_import(found_path, code)
    steps.append(step3)
    if step3.status == 'error':
        return steps

    # Step 4: Execute ETL
    step4 = execute_etl()
    steps.append(step4)
    if step4.status == 'error':
        # ETL failed — do NOT proceed to Sage
        return steps

    # Step 5: Backup CSV
    step5 = backup_csv()
    steps.append(step5)
    # Continue even if backup warning (non-critical)

    # Step 6: Send to Sage X3
    step6 = send_to_sage()
    steps.append(step6)

    return steps
