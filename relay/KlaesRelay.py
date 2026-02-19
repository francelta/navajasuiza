"""
╔══════════════════════════════════════════════════════════════╗
║   KlaesRelay.py — Lightweight HTTP Bridge Agent             ║
║   Runs on the SageX3V12 Windows Server                      ║
║   Provides HTTP endpoints for NavajaSuiza Django backend    ║
║══════════════════════════════════════════════════════════════╝

Usage:
    python KlaesRelay.py                    # Dev mode
    KlaesRelay.exe                          # Production (PyInstaller)

Endpoints:
    GET  /health                            # Health check
    GET  /fetch-xml/<codigo>                # Search & return XML content
    POST /write-csv                         # Write CSV data to import folder
    POST /execute-sql                       # Execute SQL query on Klaes DB

Build .exe:
    pip install pyinstaller flask pyodbc
    pyinstaller --onefile --name KlaesRelay KlaesRelay.py
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify

# ============================================
# CONFIGURATION — Edit these paths for your server
# ============================================
CONFIG = {
    # XML search paths (ordered by priority)
    'XML_SEARCH_PATHS': [
        r'D:\Errores\Produccion',
        r'C:\SAGE\SAGEX3\X3V12\Dossiers\PROD\Urgentes',
        r'C:\SAGE\SAGEX3\X3V12\Dossiers\PROD\Pendientes',
    ],

    # Import destination for XML
    'XML_IMPORT_PATH': r'C:\SAGE\SAGEX3\X3V12\Dossiers\PROD\IMPORT\QR',

    # CSV import destination for presupuestos
    'CSV_IMPORT_PATH': r'C:\SAGE\SAGEX3\X3V12\Dossiers\PROD\IMPORT\PRESUPUESTOS\importPresu.csv',

    # SQL Server connection string (Klaes)
    'SQL_SERVER': '192.168.2.202',
    'SQL_DATABASE': 'KlaesDB',
    'SQL_USER': 'sa',
    'SQL_PASSWORD': 'your_password_here',
    'SQL_DRIVER': '{ODBC Driver 17 for SQL Server}',

    # Relay server
    'HOST': '0.0.0.0',
    'PORT': 5000,

    # Security: simple shared token
    'AUTH_TOKEN': 'navajasuiza-relay-2026',
}

# ============================================
# Logging
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('KlaesRelay.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger('KlaesRelay')

# ============================================
# Flask App
# ============================================
app = Flask(__name__)


def check_auth():
    """Validate the Bearer token from the request."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return False
    token = auth[7:]
    return token == CONFIG['AUTH_TOKEN']


def auth_required(f):
    """Decorator to enforce token authentication."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth():
            return jsonify({'error': 'Token inválido o ausente.'}), 401
        return f(*args, **kwargs)
    return decorated


# ============================================
# Endpoints
# ============================================

@app.route('/health', methods=['GET'])
def health():
    """Health check — no auth required."""
    return jsonify({
        'status': 'ok',
        'service': 'KlaesRelay',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'hostname': os.environ.get('COMPUTERNAME', 'unknown'),
    })


@app.route('/fetch-xml/<codigo>', methods=['GET'])
@auth_required
def fetch_xml(codigo):
    """
    Search for {codigo}.xml in the configured paths.
    Returns the XML content as text if found.
    """
    # Sanitize: only allow alphanumeric codes
    if not codigo or not codigo.replace('-', '').replace('_', '').isalnum():
        return jsonify({'error': f'Código inválido: "{codigo}"'}), 400

    filename = f'{codigo.upper()}.xml'
    logger.info(f'[FETCH-XML] Searching: {filename}')

    for i, search_path in enumerate(CONFIG['XML_SEARCH_PATHS'], 1):
        full_path = Path(search_path) / filename

        # Security: ensure resolved path stays within search directory
        try:
            resolved = full_path.resolve()
            base_resolved = Path(search_path).resolve()
            if not str(resolved).startswith(str(base_resolved)):
                logger.warning(f'Path traversal attempt blocked: {codigo}')
                return jsonify({'error': 'Acceso denegado.'}), 403
        except Exception:
            continue

        if full_path.exists() and full_path.is_file():
            try:
                content = full_path.read_text(encoding='utf-8')
                logger.info(f'[FETCH-XML] Found in path {i}: {full_path}')
                return jsonify({
                    'found': True,
                    'path_number': i,
                    'path': str(full_path),
                    'filename': filename,
                    'content': content,
                    'size_bytes': len(content),
                })
            except Exception as e:
                logger.error(f'[FETCH-XML] Error reading {full_path}: {e}')
                return jsonify({'error': f'Error al leer archivo: {str(e)}'}), 500

    # Not found
    logger.info(f'[FETCH-XML] Not found: {filename}')
    return jsonify({
        'found': False,
        'filename': filename,
        'searched_paths': CONFIG['XML_SEARCH_PATHS'],
    }), 404


@app.route('/write-csv', methods=['POST'])
@auth_required
def write_csv():
    """
    Receive CSV data and write it to the import file.
    Body: { "csv_content": "...csv data..." }
    """
    data = request.get_json(silent=True)
    if not data or 'csv_content' not in data:
        return jsonify({'error': 'Campo "csv_content" es obligatorio.'}), 400

    csv_content = data['csv_content']
    csv_path = Path(CONFIG['CSV_IMPORT_PATH'])

    logger.info(f'[WRITE-CSV] Writing {len(csv_content)} chars to {csv_path}')

    try:
        # Ensure parent directory exists
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV
        csv_path.write_text(csv_content, encoding='utf-8')

        # Also create a timestamped backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'importPresu_{timestamp}.csv'
        backup_path = csv_path.parent / backup_name
        backup_path.write_text(csv_content, encoding='utf-8')

        logger.info(f'[WRITE-CSV] Success. Backup: {backup_name}')
        return jsonify({
            'success': True,
            'path': str(csv_path),
            'backup': str(backup_path),
            'size_bytes': len(csv_content),
        })

    except Exception as e:
        logger.error(f'[WRITE-CSV] Error: {e}')
        return jsonify({'error': f'Error al escribir CSV: {str(e)}'}), 500


@app.route('/write-xml', methods=['POST'])
@auth_required
def write_xml():
    """
    Receive XML content and write it to the import folder.
    Body: { "filename": "Q1234567.xml", "content": "...xml..." }
    """
    data = request.get_json(silent=True)
    if not data or 'filename' not in data or 'content' not in data:
        return jsonify({'error': 'Campos "filename" y "content" son obligatorios.'}), 400

    filename = data['filename']
    content = data['content']
    import_dir = Path(CONFIG['XML_IMPORT_PATH'])

    # Sanitize filename
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Nombre de archivo inválido.'}), 400

    dest_path = import_dir / filename

    logger.info(f'[WRITE-XML] Writing {filename} to {import_dir}')

    try:
        import_dir.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content, encoding='utf-8')
        logger.info(f'[WRITE-XML] Success: {dest_path}')
        return jsonify({
            'success': True,
            'path': str(dest_path),
            'size_bytes': len(content),
        })
    except Exception as e:
        logger.error(f'[WRITE-XML] Error: {e}')
        return jsonify({'error': f'Error al escribir XML: {str(e)}'}), 500


@app.route('/execute-sql', methods=['POST'])
@auth_required
def execute_sql():
    """
    Execute a SQL query on the local Klaes/Sage database.
    Body: { "query": "SELECT ...", "params": {...} }
    Returns rows as list of dicts for SELECT, or affected count for UPDATE/INSERT.
    """
    data = request.get_json(silent=True)
    if not data or 'query' not in data:
        return jsonify({'error': 'Campo "query" es obligatorio.'}), 400

    query = data['query'].strip()
    params = data.get('params', {})

    # Security: block dangerous operations
    query_upper = query.upper()
    blocked_keywords = ['DROP ', 'TRUNCATE ', 'ALTER ', 'CREATE ', 'EXEC ', 'XP_']
    for keyword in blocked_keywords:
        if keyword in query_upper:
            logger.warning(f'[EXECUTE-SQL] Blocked dangerous query: {keyword}')
            return jsonify({'error': f'Operación bloqueada: "{keyword.strip()}" no permitido.'}), 403

    logger.info(f'[EXECUTE-SQL] Executing: {query[:100]}...')

    try:
        import pyodbc

        conn_str = (
            f"DRIVER={CONFIG['SQL_DRIVER']};"
            f"SERVER={CONFIG['SQL_SERVER']};"
            f"DATABASE={CONFIG['SQL_DATABASE']};"
            f"UID={CONFIG['SQL_USER']};"
            f"PWD={CONFIG['SQL_PASSWORD']};"
            f"TrustServerCertificate=yes;"
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Substitute named params → positional (pyodbc uses ?)
        processed_query = query
        param_values = []
        for key, val in params.items():
            processed_query = processed_query.replace(f':{key}', '?')
            param_values.append(val)

        cursor.execute(processed_query, param_values)

        is_select = query_upper.startswith('SELECT')

        if is_select:
            columns = [desc[0] for desc in cursor.description]
            rows = []
            for row in cursor.fetchall():
                row_dict = {}
                for i, col in enumerate(columns):
                    val = row[i]
                    # Convert non-serializable types
                    if isinstance(val, (datetime,)):
                        val = val.isoformat()
                    elif isinstance(val, bytes):
                        val = val.hex()
                    elif hasattr(val, '__float__'):
                        val = float(val)
                    row_dict[col] = val
                rows.append(row_dict)

            conn.close()
            logger.info(f'[EXECUTE-SQL] SELECT returned {len(rows)} rows')
            return jsonify({
                'success': True,
                'type': 'select',
                'columns': columns,
                'rows': rows,
                'row_count': len(rows),
            })
        else:
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            logger.info(f'[EXECUTE-SQL] Modified {affected} rows')
            return jsonify({
                'success': True,
                'type': 'modify',
                'affected_rows': affected,
            })

    except ImportError:
        return jsonify({'error': 'pyodbc no está instalado en el servidor.'}), 500
    except Exception as e:
        logger.error(f'[EXECUTE-SQL] Error: {e}')
        return jsonify({'error': f'Error SQL: {str(e)}'}), 500


# ============================================
# Startup
# ============================================
if __name__ == '__main__':
    print(r"""
    ╔══════════════════════════════════════════╗
    ║   🔧 KlaesRelay v1.0 — Bridge Agent    ║
    ║   NavajaSuiza Project                    ║
    ╚══════════════════════════════════════════╝
    """)
    print(f"  🌐 Server: http://{CONFIG['HOST']}:{CONFIG['PORT']}")
    print(f"  🔑 Token:  {CONFIG['AUTH_TOKEN'][:8]}...")
    print(f"  📁 XML Paths: {len(CONFIG['XML_SEARCH_PATHS'])} configured")
    print(f"  🗄️  SQL Server: {CONFIG['SQL_SERVER']}/{CONFIG['SQL_DATABASE']}")
    print()

    app.run(
        host=CONFIG['HOST'],
        port=CONFIG['PORT'],
        debug=False,
        threaded=True,
    )
