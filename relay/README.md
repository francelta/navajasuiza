# KlaesRelay — HTTP Bridge Agent

## ¿Qué es?

Un servidor HTTP minimalista que corre **dentro del servidor SageX3V12 (Windows)**.
Actúa como puente: la app NavajaSuiza (Django) le pide datos por HTTP en lugar de acceder a las carpetas del servidor directamente.

## Requisitos (solo para desarrollo)

```
Python 3.10+
pip install flask pyodbc pyinstaller
```

## Generar el `.exe` (una sola vez)

```powershell
cd relay/
pip install -r requirements.txt
pip install pyinstaller

# Generar ejecutable único
pyinstaller --onefile --name KlaesRelay --icon=NONE KlaesRelay.py

# El .exe se genera en:
# relay/dist/KlaesRelay.exe
```

## Desplegar en el servidor

1. Copia `dist/KlaesRelay.exe` al servidor Windows (ej: `C:\NavajaSuiza\`)
2. Doble clic para ejecutar (o crear un servicio Windows)
3. El relay escucha en `http://0.0.0.0:5000`

## Configuración

Edita las variables dentro del `CONFIG` dict en `KlaesRelay.py` **antes de generar el .exe**:

| Variable | Descripción |
|----------|-------------|
| `XML_SEARCH_PATHS` | Las 3 rutas donde buscar XMLs |
| `XML_IMPORT_PATH` | Carpeta destino para XMLs |
| `CSV_IMPORT_PATH` | Ruta del CSV de import presupuestos |
| `SQL_SERVER` | IP/hostname del SQL Server |
| `SQL_DATABASE` | Nombre de la BD Klaes |
| `SQL_USER` / `SQL_PASSWORD` | Credenciales SQL |
| `AUTH_TOKEN` | Token compartido con Django |
| `PORT` | Puerto (default: 5000) |

## Endpoints

| Method | Path | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check (sin auth) |
| GET | `/fetch-xml/<codigo>` | Busca XML y devuelve contenido |
| POST | `/write-csv` | Escribe CSV a la carpeta import |
| POST | `/write-xml` | Escribe XML a la carpeta import |
| POST | `/execute-sql` | Ejecuta query SQL (SELECT/UPDATE) |

## Seguridad

- **Token Bearer** requerido en todas las rutas excepto `/health`
- **Path traversal** protegido en fetch/write
- **SQL bloqueado**: DROP, TRUNCATE, ALTER, CREATE, EXEC, XP_
