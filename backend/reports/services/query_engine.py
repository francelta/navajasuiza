"""
[AGENTE_DATA_ENGINEER] — QueryEngine: Multi-Source Data Loader.

Executes ALL AppLoadScripts of a ReportApp sequentially,
connecting to each script's DBConnection separately.
Returns a combined data model: { script_name: { columns, rows, row_count } }
"""
import logging
from datetime import datetime

import pandas as pd

from reports.models import ReportApp

logger = logging.getLogger(__name__)

MAX_RESULT_ROWS = 500

DRIVER_MAP = {
    'sqlserver': '{ODBC Driver 17 for SQL Server}',
    'mysql': '{MySQL ODBC 8.0 Unicode Driver}',
    'postgresql': '{PostgreSQL Unicode}',
}

# Blocked SQL keywords
BLOCKED_KEYWORDS = ['DROP ', 'TRUNCATE ', 'ALTER ', 'CREATE ', 'DELETE ', 'INSERT ', 'UPDATE ', 'EXEC ', 'XP_']


def _build_connection_string(conn):
    driver = DRIVER_MAP.get(conn.engine)
    if not driver:
        raise ValueError(f'Motor no soportado: "{conn.engine}"')

    if conn.engine == 'sqlserver':
        return (
            f'DRIVER={driver};SERVER={conn.host},{conn.port};'
            f'DATABASE={conn.database};UID={conn.username};PWD={conn.password};'
            f'TrustServerCertificate=yes;'
        )
    else:
        return (
            f'DRIVER={driver};SERVER={conn.host};PORT={conn.port};'
            f'DATABASE={conn.database};UID={conn.username};PWD={conn.password};'
        )


def _classify_columns(df):
    """Classify DataFrame columns by type."""
    cols = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            cols.append({'name': col, 'type': 'numeric'})
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            cols.append({'name': col, 'type': 'datetime'})
        else:
            cols.append({'name': col, 'type': 'categorical'})
    return cols


def _df_to_records(df, max_rows=MAX_RESULT_ROWS):
    """Convert DataFrame to list of dicts for JSON serialization."""
    rows = []
    for _, row in df.head(max_rows).iterrows():
        record = {}
        for col, val in row.items():
            if pd.isna(val):
                record[col] = None
            elif isinstance(val, (int, float)):
                record[col] = float(val) if isinstance(val, float) else int(val)
            else:
                record[col] = str(val)
        rows.append(record)
    return rows


def test_connection(db_connection):
    """Test a DBConnection. Returns (success, message)."""
    try:
        import pyodbc
        conn_str = _build_connection_string(db_connection)
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        logger.info(f'[QUERY_ENGINE] Test OK: {db_connection.name}')
        return True, 'Conexión exitosa.'
    except Exception as e:
        msg = str(e)
        logger.warning(f'[QUERY_ENGINE] Test FAILED: {db_connection.name} — {msg}')
        return False, f'Error: {msg}'


def execute_single_script(script):
    """
    Execute a single AppLoadScript against its DBConnection.
    Returns dict with columns, rows, row_count, execution_time_ms.
    Updates the script's cached metadata.
    """
    import pyodbc

    query = script.query_text.strip()
    if not query:
        raise ValueError(f'Script "{script.name}": query vacía.')

    # Security check
    query_upper = query.upper()
    for kw in BLOCKED_KEYWORDS:
        if kw in query_upper:
            raise ValueError(f'Operación bloqueada en "{script.name}": "{kw.strip()}"')

    conn_model = script.connection
    start = datetime.now()

    try:
        conn_str = _build_connection_string(conn_model)
        conn = pyodbc.connect(conn_str, timeout=30)
        df = pd.read_sql(query, conn)
        conn.close()

        elapsed = int((datetime.now() - start).total_seconds() * 1000)

        # Update cached metadata
        script.last_row_count = len(df)
        script.last_executed_at = datetime.now()
        script.last_error = ''
        script.save(update_fields=['last_row_count', 'last_executed_at', 'last_error'])

        logger.info(f'[QUERY_ENGINE] "{script.name}" → {len(df)} rows in {elapsed}ms')

        return {
            'columns': _classify_columns(df),
            'rows': _df_to_records(df),
            'row_count': len(df),
            'showing': min(len(df), MAX_RESULT_ROWS),
            'execution_time_ms': elapsed,
        }

    except Exception as e:
        script.last_error = str(e)
        script.save(update_fields=['last_error'])
        raise ValueError(f'Error en "{script.name}": {str(e)}')


def execute_app_data_load(app_id):
    """
    Execute ALL AppLoadScripts of a ReportApp sequentially.

    Returns:
    {
        "tables": {
            "script_name": { "columns": [...], "rows": [...], "row_count": N, ... },
            ...
        },
        "log": [
            {"script": "name", "status": "ok|error", "rows": N, "time_ms": T, "message": "..."}
        ],
        "total_scripts": N,
        "success_count": N
    }
    """
    try:
        app = ReportApp.objects.prefetch_related('scripts__connection').get(pk=app_id)
    except ReportApp.DoesNotExist:
        raise ValueError(f'ReportApp ID={app_id} no existe.')

    scripts = app.scripts.all().order_by('order', 'id')
    if not scripts.exists():
        raise ValueError('Esta aplicación no tiene scripts de carga configurados.')

    tables = {}
    log = []
    success_count = 0

    for script in scripts:
        try:
            result = execute_single_script(script)
            tables[script.name] = result
            log.append({
                'script': script.name,
                'connection': script.connection.name,
                'status': 'ok',
                'rows': result['row_count'],
                'time_ms': result['execution_time_ms'],
                'message': f'{result["row_count"]} filas extraídas.',
            })
            success_count += 1
        except ValueError as e:
            log.append({
                'script': script.name,
                'connection': script.connection.name,
                'status': 'error',
                'rows': 0,
                'time_ms': 0,
                'message': str(e),
            })
            logger.error(f'[QUERY_ENGINE] Script "{script.name}" failed: {e}')

    return {
        'tables': tables,
        'log': log,
        'total_scripts': len(scripts),
        'success_count': success_count,
    }
