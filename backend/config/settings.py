"""
Django settings for NavajaSuiza project.
Enterprise-grade local intranet application.
"""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'navajasuiza-dev-secret-key-change-in-production-2024')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Local apps
    'users',
    'core',
    'tools',
    'klaes_integration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database — SQLite for rapid local dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# SimpleJWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS — Only allow our Vue frontend
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True

# ============================================
# SMTP Email — Correo Corporativo (Dinahosting)
# ============================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'mail.acristalia.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'NavajaSuiza <no-reply@acristalia.com>')
EMAIL_TIMEOUT = 10  # seconds — fail fast on SMTP issues

# Frontend URL for welcome email links
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# ============================================
# Klaes XML Reprocessing — Tarea 1
# ============================================
KLAES_SEARCH_PATHS = [
    os.getenv('PATH_BUSQUEDA_1', ''),
    os.getenv('PATH_BUSQUEDA_2', ''),
    os.getenv('PATH_BUSQUEDA_3', ''),
]
KLAES_IMPORT_PATH = os.getenv('PATH_IMPORTACION_QR', '')
KLAES_CSV_OUTPUT_PATH = os.getenv('PATH_OUTPUT_CSV', '')
KLAES_ETL_COMMAND = os.getenv('CMD_ETL_KLAES_SAGE', '')

# ============================================
# Sage X3 Web Service
# ============================================
SAGE_WS_URL = os.getenv('SAGE_WS_URL', '')
SAGE_WS_USER = os.getenv('SAGE_WS_USER', '')
SAGE_WS_PASSWORD = os.getenv('SAGE_WS_PASSWORD', '')
SAGE_POOL_ALIAS = os.getenv('SAGE_POOL_ALIAS', 'PRODUCTION')
SAGE_WS_LANGUAGE = os.getenv('SAGE_WS_LANGUAGE', 'SPA')
SAGE_WS_IMPORT_TEMPLATE = os.getenv('SAGE_WS_IMPORT_TEMPLATE', 'KLAES')

# ============================================
# Klaes SQL Server — ODBC Connection
# ============================================
_klaes_server = os.getenv('KLAES_DB_SERVER', '')
_klaes_db = os.getenv('KLAES_DB_NAME', '')
_klaes_user = os.getenv('KLAES_DB_USER', '')
_klaes_pass = os.getenv('KLAES_DB_PASSWORD', '')
_klaes_driver = os.getenv('KLAES_DB_DRIVER', 'ODBC+Driver+17+for+SQL+Server')

if _klaes_server and _klaes_db:
    KLAES_DB_CONNECTION_STRING = (
        f'mssql+pyodbc://{_klaes_user}:{_klaes_pass}'
        f'@{_klaes_server}/{_klaes_db}'
        f'?driver={_klaes_driver}&TrustServerCertificate=yes'
    )
else:
    KLAES_DB_CONNECTION_STRING = ''

