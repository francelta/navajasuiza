"""
KlaesReprocessingService — HTTP Relay Architecture.

Pipeline (via KlaesRelay bridge on SageX3 server):
  1. Validate production code (Q/R + 7 digits)
  2. Fetch XML via relay HTTP (GET /fetch-xml/<code>)
  3. Write XML to import folder via relay (POST /write-xml)
  4. Execute ETL (local or via relay)
  5. Backup CSV (handled by relay on write)
  6. Send to Sage X3 via Web Service

[AGENTE_BACKEND] Uses `requests` instead of shutil/subprocess.
All file operations are delegated to the KlaesRelay running on the server.
"""
import re
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Regex: Q or R followed by exactly 7 digits
CODE_PATTERN = re.compile(r'^[QR]\d{7}$')


class KlaesStepResult:
    """Represents the result of a single pipeline step."""

    def __init__(self, step, status, message, detail=None):
        self.step = step
        self.status = status      # 'ok', 'error', 'warning', 'pending'
        self.message = message
        self.detail = detail

    def to_dict(self):
        d = {
            'step': self.step,
            'status': self.status,
            'message': self.message,
        }
        if self.detail:
            d['detail'] = self.detail
        return d


def _relay_url(path):
    """Build the full URL for a relay endpoint."""
    base = settings.KLAES_RELAY_URL.rstrip('/')
    return f'{base}/{path.lstrip("/")}'


def _relay_headers():
    """Return auth headers for the relay."""
    return {
        'Authorization': f'Bearer {settings.KLAES_RELAY_TOKEN}',
        'Content-Type': 'application/json',
    }


def _check_relay_config():
    """Verify relay URL and token are configured."""
    if not getattr(settings, 'KLAES_RELAY_URL', ''):
        raise RuntimeError(
            'KLAES_RELAY_URL no está configurada. '
            'Configura la URL del KlaesRelay en el archivo .env.'
        )
    if not getattr(settings, 'KLAES_RELAY_TOKEN', ''):
        raise RuntimeError(
            'KLAES_RELAY_TOKEN no está configurado. '
            'Configura el token del KlaesRelay en el archivo .env.'
        )


# ============================================
# Pipeline Steps
# ============================================

def validate_code(code):
    """Step 1: Validate production code format."""
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


def fetch_xml(code):
    """
    Step 2: Fetch XML from the server via KlaesRelay.
    GET http://relay:5000/fetch-xml/<code>
    Returns XML content and metadata.
    """
    _check_relay_config()
    url = _relay_url(f'fetch-xml/{code.upper()}')

    try:
        resp = requests.get(url, headers=_relay_headers(), timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            return KlaesStepResult(
                step=2,
                status='ok',
                message=f'Archivo encontrado en Ruta {data.get("path_number", "?")}',
                detail={
                    'filename': data.get('filename'),
                    'path': data.get('path'),
                    'content': data.get('content'),
                    'size_bytes': data.get('size_bytes'),
                },
            )
        elif resp.status_code == 404:
            return KlaesStepResult(
                step=2,
                status='error',
                message='El archivo no se encuentra en las carpetas del servidor.',
                detail=resp.json() if resp.text else None,
            )
        elif resp.status_code == 401:
            return KlaesStepResult(
                step=2,
                status='error',
                message='Token de relay inválido. Verifica KLAES_RELAY_TOKEN.',
            )
        else:
            return KlaesStepResult(
                step=2,
                status='error',
                message=f'Relay respondió con HTTP {resp.status_code}.',
                detail={'body': resp.text[:300]},
            )

    except requests.exceptions.ConnectionError:
        return KlaesStepResult(
            step=2,
            status='error',
            message='No se pudo conectar con el KlaesRelay. ¿Está ejecutándose en el servidor?',
        )
    except requests.exceptions.Timeout:
        return KlaesStepResult(
            step=2,
            status='error',
            message='Conexión con el relay excedió el tiempo límite (15s).',
        )
    except Exception as e:
        return KlaesStepResult(
            step=2,
            status='error',
            message=f'Error inesperado al contactar relay: {str(e)}',
        )


def write_xml_to_import(code, xml_content):
    """
    Step 3: Write XML to the import folder via KlaesRelay.
    POST http://relay:5000/write-xml
    """
    _check_relay_config()
    url = _relay_url('write-xml')
    payload = {
        'filename': f'{code.upper()}.xml',
        'content': xml_content,
    }

    try:
        resp = requests.post(url, json=payload, headers=_relay_headers(), timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            return KlaesStepResult(
                step=3,
                status='ok',
                message='Archivo copiado a carpeta de importación.',
                detail={'destination': data.get('path')},
            )
        else:
            error = resp.json().get('error', f'HTTP {resp.status_code}') if resp.text else f'HTTP {resp.status_code}'
            return KlaesStepResult(
                step=3,
                status='error',
                message=f'Error al escribir XML: {error}',
            )

    except requests.exceptions.ConnectionError:
        return KlaesStepResult(
            step=3,
            status='error',
            message='No se pudo conectar con el KlaesRelay para escribir XML.',
        )
    except Exception as e:
        return KlaesStepResult(
            step=3,
            status='error',
            message=f'Error al escribir XML: {str(e)}',
        )


def write_csv_to_import(csv_content):
    """
    Step 4: Write CSV data to the import folder via KlaesRelay.
    POST http://relay:5000/write-csv
    """
    _check_relay_config()
    url = _relay_url('write-csv')

    try:
        resp = requests.post(
            url,
            json={'csv_content': csv_content},
            headers=_relay_headers(),
            timeout=15,
        )

        if resp.status_code == 200:
            data = resp.json()
            return KlaesStepResult(
                step=4,
                status='ok',
                message='CSV escrito en carpeta de importación.',
                detail={
                    'path': data.get('path'),
                    'backup': data.get('backup'),
                },
            )
        else:
            error = resp.json().get('error', f'HTTP {resp.status_code}') if resp.text else f'HTTP {resp.status_code}'
            return KlaesStepResult(
                step=4,
                status='error',
                message=f'Error al escribir CSV: {error}',
            )

    except requests.exceptions.ConnectionError:
        return KlaesStepResult(
            step=4,
            status='error',
            message='No se pudo conectar con el KlaesRelay para escribir CSV.',
        )
    except Exception as e:
        return KlaesStepResult(
            step=4,
            status='error',
            message=f'Error al escribir CSV: {str(e)}',
        )


def send_to_sage():
    """
    Step 5: Import data into Sage X3 via Web Service (SOAP).
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
            step=5,
            status='error',
            message='Sage Web Service URL no configurada (SAGE_WS_URL).',
        )

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
        from requests.auth import HTTPBasicAuth

        response = requests.post(
            ws_url,
            data=soap_body,
            headers={'Content-Type': 'text/xml; charset=utf-8'},
            auth=HTTPBasicAuth(ws_user, ws_password),
            timeout=60,
            verify=False,
        )

        if response.status_code == 200:
            if '<faultcode>' in response.text:
                return KlaesStepResult(
                    step=5,
                    status='error',
                    message='Sage X3 devolvió un error SOAP.',
                    detail={'soap_fault': response.text[:300]},
                )
            return KlaesStepResult(
                step=5,
                status='ok',
                message='Datos importados en Sage X3 correctamente.',
                detail={'http_status': response.status_code},
            )
        else:
            return KlaesStepResult(
                step=5,
                status='error',
                message=f'Sage X3 respondió con HTTP {response.status_code}.',
                detail={'response_body': response.text[:300]},
            )

    except requests.exceptions.ConnectionError:
        return KlaesStepResult(
            step=5,
            status='error',
            message='No se pudo conectar con Sage X3. Verifica SAGE_WS_URL.',
        )
    except requests.exceptions.Timeout:
        return KlaesStepResult(
            step=5,
            status='error',
            message='Conexión con Sage X3 excedió el tiempo límite (60s).',
        )
    except Exception as e:
        return KlaesStepResult(
            step=5,
            status='error',
            message=f'Error inesperado con Sage X3: {str(e)}',
        )


def run_pipeline(code):
    """
    Execute the Klaes reprocessing pipeline via HTTP Relay.
    Returns a list of step results. Stops on critical errors.

    New flow:
      1. Validate code
      2. Fetch XML from server (via relay)
      3. Write XML to import folder (via relay)
      4. (CSV write — if needed, via relay)
      5. Send to Sage X3 (SOAP direct)
    """
    steps = []

    # Step 1: Validate code
    step1 = validate_code(code)
    steps.append(step1)
    if step1.status == 'error':
        return steps

    code = code.upper()

    # Step 2: Fetch XML from server via relay
    step2 = fetch_xml(code)
    steps.append(step2)
    if step2.status == 'error':
        return steps

    xml_content = step2.detail.get('content', '')

    # Step 3: Write XML to import folder via relay
    step3 = write_xml_to_import(code, xml_content)
    steps.append(step3)
    if step3.status == 'error':
        return steps

    # Step 4: Send to Sage X3
    step4 = send_to_sage()
    steps.append(step4)

    return steps
