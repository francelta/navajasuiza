"""
Environment Configuration Service — .env reader/writer.
Reads and writes the .env file safely, preserving comments and structure.

[AGENTE_DEVOPS] — REQUIRED_ENV_VARS schema defined here.
[AGENTE_SEGURIDAD] — Never returns real values for sensitive keys.
"""
import os
import re
from pathlib import Path
from django.conf import settings

# ============================================
# REQUIRED_ENV_VARS — Complete schema
# ============================================
# Each entry: (key, label, group, is_sensitive, placeholder)
REQUIRED_ENV_VARS = [
    # --- Django Core ---
    ('SECRET_KEY', 'Clave Secreta Django', 'Django', True, 'una-clave-aleatoria-muy-larga'),
    ('DEBUG', 'Modo Debug', 'Django', False, 'True'),

    # --- SMTP Email (Dinahosting) ---
    ('EMAIL_HOST', 'Servidor de Correo', 'Email SMTP', False, 'mail.acristalia.com'),
    ('EMAIL_PORT', 'Puerto SMTP', 'Email SMTP', False, '465'),
    ('EMAIL_USE_SSL', 'Usar SSL', 'Email SMTP', False, 'True'),
    ('EMAIL_USE_TLS', 'Usar TLS', 'Email SMTP', False, 'False'),
    ('EMAIL_HOST_USER', 'Usuario SMTP', 'Email SMTP', False, 'no-reply@acristalia.com'),
    ('EMAIL_HOST_PASSWORD', 'Contraseña SMTP', 'Email SMTP', True, ''),
    ('DEFAULT_FROM_EMAIL', 'Remitente por Defecto', 'Email SMTP', False, 'NavajaSuiza <no-reply@acristalia.com>'),
    ('FRONTEND_URL', 'URL del Frontend', 'Email SMTP', False, 'http://localhost:5173'),

    # --- Klaes / ETL (Tarea 1) ---
    ('PATH_BUSQUEDA_1', 'Ruta Búsqueda XML #1', 'Klaes / ETL', False, '/ruta/carpeta/produccion1'),
    ('PATH_BUSQUEDA_2', 'Ruta Búsqueda XML #2', 'Klaes / ETL', False, '/ruta/carpeta/produccion2'),
    ('PATH_BUSQUEDA_3', 'Ruta Búsqueda XML #3', 'Klaes / ETL', False, '/ruta/carpeta/produccion3'),
    ('PATH_IMPORTACION_QR', 'Carpeta Importación XML', 'Klaes / ETL', False, '/ruta/carpeta/importacion'),
    ('PATH_OUTPUT_CSV', 'Carpeta Salida CSV', 'Klaes / ETL', False, '/ruta/carpeta/csv_output'),
    ('CMD_ETL_KLAES_SAGE', 'Comando ETL', 'Klaes / ETL', False, 'C:/Klaes/ETL/klaes_to_sage.exe'),

    # --- KlaesRelay (HTTP Bridge) ---
    ('KLAES_RELAY_URL', 'URL del Relay', 'KlaesRelay', False, 'http://192.168.2.202:5000'),
    ('KLAES_RELAY_TOKEN', 'Token del Relay', 'KlaesRelay', True, ''),

    # --- Sage X3 Web Service ---
    ('SAGE_WS_URL', 'URL Web Service Sage', 'Sage X3', False, 'http://servidor-sage:8124/soap-wsdl/...'),
    ('SAGE_WS_USER', 'Usuario Sage', 'Sage X3', False, 'admin'),
    ('SAGE_WS_PASSWORD', 'Contraseña Sage', 'Sage X3', True, ''),
    ('SAGE_POOL_ALIAS', 'Pool Alias', 'Sage X3', False, 'PRODUCTION'),
    ('SAGE_WS_LANGUAGE', 'Idioma Sage', 'Sage X3', False, 'SPA'),
    ('SAGE_WS_IMPORT_TEMPLATE', 'Plantilla Importación', 'Sage X3', False, 'KLAES'),

    # --- Klaes SQL Server (ODBC) ---
    ('KLAES_DB_SERVER', 'Servidor SQL Server', 'Klaes SQL Server', False, '192.168.1.100'),
    ('KLAES_DB_NAME', 'Nombre Base de Datos', 'Klaes SQL Server', False, 'KlaesDB'),
    ('KLAES_DB_USER', 'Usuario SQL', 'Klaes SQL Server', False, 'sa'),
    ('KLAES_DB_PASSWORD', 'Contraseña SQL', 'Klaes SQL Server', True, ''),
    ('KLAES_DB_DRIVER', 'Driver ODBC', 'Klaes SQL Server', False, 'ODBC+Driver+17+for+SQL+Server'),
]


def _get_env_path():
    """Returns the absolute path to the .env file."""
    return settings.BASE_DIR / '.env'


def _parse_env_file():
    """
    Parse the .env file and return:
    - lines: list of raw lines (preserves comments, blank lines)
    - values: dict of {KEY: value} for existing keys
    """
    env_path = _get_env_path()
    lines = []
    values = {}

    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                key, _, value = stripped.partition('=')
                key = key.strip()
                value = value.strip()
                values[key] = value

    return lines, values


def get_env_status():
    """
    GET status: Returns the configuration status for all required vars.
    [AGENTE_SEGURIDAD] — Sensitive values are NEVER returned.
    """
    _, current_values = _parse_env_file()

    result = []
    for key, label, group, is_sensitive, placeholder in REQUIRED_ENV_VARS:
        raw_value = current_values.get(key, '')
        # A variable is "set" if it exists, has a non-empty value,
        # and is not a placeholder-like default
        is_placeholder = raw_value in (
            '', 'tu_contraseña_smtp_aqui', 'tu_password_sage',
            'navajasuiza-cambia-esta-clave-en-produccion',
            'tu_password_sql_server',
        )
        is_set = bool(raw_value) and not is_placeholder

        entry = {
            'key': key,
            'label': label,
            'group': group,
            'is_sensitive': is_sensitive,
            'is_set': is_set,
            'placeholder': placeholder,
        }

        # Only include the value for non-sensitive vars that are set
        if is_set and not is_sensitive:
            entry['current_value'] = raw_value

        result.append(entry)

    return result


def update_env_var(key, value):
    """
    POST update: Write a single key=value to the .env file.
    - If the key exists and already has a real value → REJECT
    - If the key exists but is empty/placeholder → UPDATE in place
    - If the key doesn't exist → APPEND at the end
    Preserves comments and structure.
    """
    # Validate key is in our schema
    valid_keys = {k for k, *_ in REQUIRED_ENV_VARS}
    if key not in valid_keys:
        return False, f'Variable "{key}" no está en el schema permitido.'

    env_path = _get_env_path()
    lines, current_values = _parse_env_file()

    current_raw = current_values.get(key, '')
    is_placeholder = current_raw in (
        '', 'tu_contraseña_smtp_aqui', 'tu_password_sage',
        'navajasuiza-cambia-esta-clave-en-produccion',
        'tu_password_sql_server',
    )
    has_real_value = bool(current_raw) and not is_placeholder

    if has_real_value:
        return False, f'"{key}" ya tiene un valor configurado. No se puede sobreescribir.'

    # Sanitize value — no newlines or special chars that break .env
    value = value.strip().replace('\n', '').replace('\r', '')

    # Try to find and replace the line
    found = False
    pattern = re.compile(rf'^{re.escape(key)}\s*=')
    new_lines = []
    for line in lines:
        if pattern.match(line.strip()):
            new_lines.append(f'{key}={value}\n')
            found = True
        else:
            new_lines.append(line)

    if not found:
        # Append at the end
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines.append('\n')
        new_lines.append(f'{key}={value}\n')

    # Create .env if it doesn't exist
    if not env_path.exists():
        env_path.parent.mkdir(parents=True, exist_ok=True)

    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    return True, f'"{key}" configurado correctamente.'
