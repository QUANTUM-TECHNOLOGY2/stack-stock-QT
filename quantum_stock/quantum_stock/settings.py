"""
Configuration Django - QUANTUM TECHNOLOGY - Gestion de stock
"""
from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# Sécurité / Debug
# ------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-a-changer")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# ------------------------------------------------------------------
# Applications
# ------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    

    # Tiers
    "widget_tweaks",
    "django_htmx",
    "django_celery_beat",

    # Applications internes
    "accounts",
    "catalog",
    "stock",
    "reservations",
    "commandes",
    "workflow",
    "notifications",
    "audit",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "audit.middleware.AuditMiddleware",
]

ROOT_URLCONF = "quantum_stock.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "notifications.context_processors.notifications_non_lues",
            ],
        },
    },
]

WSGI_APPLICATION = "quantum_stock.wsgi.application"
ASGI_APPLICATION = "quantum_stock.asgi.application"

# ------------------------------------------------------------------
# Base de données - PostgreSQL sur Supabase
# ------------------------------------------------------------------
DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql://postgres:postgres@localhost:5432/quantum_stock",
)
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG)
}

# ------------------------------------------------------------------
# Authentification
# ------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "accounts:login"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------
# Internationalisation
# ------------------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Porto-Novo"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Fichiers statiques / médias
# ------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------
# Email
# ------------------------------------------------------------------
if config("EMAIL_HOST", default=""):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
else:
    # Aucun serveur SMTP configuré : les emails s'affichent dans la console (dev)
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="QUANTUM TECHNOLOGY <no-reply@quantum-technology.com>")

# ------------------------------------------------------------------
# Cache / Redis / Celery
# ------------------------------------------------------------------
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ------------------------------------------------------------------
# Sécurité additionnelle
# ------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # nécessaire pour HTMX qui lit le cookie côté JS
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

# ------------------------------------------------------------------
# Charte graphique (exposée aux templates si besoin via context processor)
# ------------------------------------------------------------------
QUANTUM_COLORS = {
    "rouge": "#D61C4E",
    "bleu": "#293462",
    "blanc": "#FFFFFF",
}

# ------------------------------------------------------------------
# Pagination par défaut
# ------------------------------------------------------------------
DEFAULT_PAGE_SIZE = 25
