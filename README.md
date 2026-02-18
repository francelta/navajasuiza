<div align="center">

# 🔧 NavajaSuiza

### Sistema de Gestión Local — Acristalia

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![Sage X3](https://img.shields.io/badge/Sage-X3_Integration-00DC00?style=for-the-badge&logo=sage&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

---

**Panel empresarial de intranet** para gestión de empleados, automatización de procesos Klaes/Sage X3, y herramientas corporativas internas.

</div>

---

## 📋 Características

| Módulo | Descripción |
|--------|-------------|
| 🔐 **Autenticación JWT** | Login corporativo, roles (SuperAdmin/Admin/Empleado), route guards |
| 👥 **Gestión de Usuarios** | Alta de empleados con envío automático de credenciales por email |
| 📧 **SMTP Corporativo** | Integración con Dinahosting (`@acristalia.com`) |
| 📄 **Reprocesamiento Klaes** | Pipeline XML → ETL → CSV backup → Sage X3 (SOAP) |
| 🛡️ **Seguridad** | Path traversal protection, sanitización, CORS, tokens rotativos |

---

## 🚀 Instalación

### Requisitos previos
- Python 3.12+
- Node.js 18+
- npm 9+

### 1. Clonar repositorio

```bash
git clone https://github.com/francelta/navajasuiza.git
cd navajasuiza
```

### 2. Backend (Django)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py create_superadmin
python manage.py runserver
```

> 🔑 **Credenciales por defecto del SuperAdmin:**
>
> | Campo | Valor |
> |-------|-------|
> | **ID Empleado** | `ADMIN001` |
> | **Contraseña** | `admin123` |

### 3. Frontend (Vue 3)

```bash
cd frontend
npm install
npm run dev
```

> 🌐 Acceso: [http://localhost:5173](http://localhost:5173)

---

## ⚠️ Requisitos del Sistema (Windows)

> [!IMPORTANT]
> **Driver ODBC para SQL Server (Klaes)**
>
> Este proyecto utiliza `pyodbc` + `sqlalchemy` para conectar con la base de datos **Klaes (SQL Server)**.
> Si al ejecutar obtienes el error *"Data source name not found"* o *"Can't open lib 'ODBC Driver 17'"*, necesitas instalar el driver en tu máquina Windows:
>
> 📥 **[Descargar ODBC Driver 17 for SQL Server (x64)](https://go.microsoft.com/fwlink/?linkid=2137251)** — Microsoft oficial (`msodbcsql.msi`)
>
> Tras la instalación, verifica con:
> ```powershell
> odbcad32.exe   # Abre el gestor ODBC → pestaña "Drivers" → debe aparecer "ODBC Driver 17 for SQL Server"
> ```

---

## ⚙️ Configuración del Entorno

Copia el archivo de ejemplo y rellena con los valores de tu empresa:

```bash
cp backend/.env.example backend/.env
```

### Variables requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django | `mi-clave-secreta-produccion` |
| `DEBUG` | Modo debug | `True` / `False` |

#### 📧 SMTP (Dinahosting)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `EMAIL_HOST` | Servidor de correo | `mail.acristalia.com` |
| `EMAIL_PORT` | Puerto SMTP | `465` |
| `EMAIL_USE_SSL` | Usar SSL | `True` |
| `EMAIL_HOST_USER` | Cuenta emisora | `no-reply@acristalia.com` |
| `EMAIL_HOST_PASSWORD` | Contraseña SMTP | `*****` |

#### 📄 Klaes / ETL

| Variable | Descripción |
|----------|-------------|
| `PATH_BUSQUEDA_1` | Ruta de búsqueda XML #1 |
| `PATH_BUSQUEDA_2` | Ruta de búsqueda XML #2 |
| `PATH_BUSQUEDA_3` | Ruta de búsqueda XML #3 |
| `PATH_IMPORTACION_QR` | Carpeta destino importación |
| `PATH_OUTPUT_CSV` | Carpeta salida CSV post-ETL |
| `CMD_ETL_KLAES_SAGE` | Ruta al ejecutable ETL |

#### 🏭 Sage X3

| Variable | Descripción |
|----------|-------------|
| `SAGE_WS_URL` | URL del Web Service SOAP |
| `SAGE_WS_USER` | Usuario Sage |
| `SAGE_WS_PASSWORD` | Contraseña Sage |
| `SAGE_POOL_ALIAS` | Alias del pool (ej: `PRODUCTION`) |
| `SAGE_WS_IMPORT_TEMPLATE` | Plantilla importación (ej: `KLAES`) |

---

## 🏗️ Arquitectura

```
navajasuiza/
├── backend/                  # Django 5 + DRF
│   ├── config/               # Settings, URLs, WSGI
│   ├── users/                # Auth, perfiles, admin CRUD
│   ├── core/                 # Permisos, email service
│   ├── tools/                # Klaes reprocessing service
│   ├── .env.example          # Plantilla de configuración
│   └── requirements.txt
├── frontend/                 # Vue 3 + Vite + Pinia
│   ├── src/
│   │   ├── views/            # Login, Dashboard, Klaes, Admin
│   │   ├── stores/           # Auth store (Pinia)
│   │   ├── api/              # Axios instance
│   │   └── components/       # ToolButton, etc.
│   └── package.json
├── .gitignore
└── README.md
```

---

## 🔒 Seguridad

- **Credenciales** (`.env`) **nunca** se suben al repositorio
- **Path Traversal** protegido en todas las operaciones de archivos
- **JWT** con rotación automática de tokens
- **CORS** restringido a `localhost:5173`
- **Roles** con permisos granulares (SuperAdmin > Admin > Empleado)

---

## 📄 Licencia

Proyecto privado — **Acristalia** © 2026. Todos los derechos reservados.
