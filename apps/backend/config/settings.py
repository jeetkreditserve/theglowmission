from __future__ import annotations

import os
from urllib.parse import urlparse
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_int_list(name: str, default: str) -> list[int]:
    values: list[int] = []
    for item in env(name, default).split(","):
        item = item.strip()
        if item:
            values.append(int(item))
    return values


SECRET_KEY = env("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = [host.strip() for host in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,backend").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "storages",
    "apps.common",
    "apps.accounts",
    "apps.contacts",
    "apps.content",
    "apps.campaigns",
    "apps.appointments",
    "apps.notifications",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = env("DATABASE_URL")
if DATABASE_URL:
    parsed_database_url = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed_database_url.path.lstrip("/"),
            "HOST": parsed_database_url.hostname or "postgres",
            "PORT": parsed_database_url.port or 5432,
            "USER": parsed_database_url.username or "",
            "PASSWORD": parsed_database_url.password or "",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB", "theglowmission"),
            "USER": env("POSTGRES_USER", "theglowmission"),
            "PASSWORD": env("POSTGRES_PASSWORD", "theglowmission"),
            "HOST": env("POSTGRES_HOST", "postgres"),
            "PORT": env("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in env("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in env("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = env("AWS_SESSION_TOKEN") or None
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", "ap-south-1")
AWS_MEDIA_LOCATION = env("AWS_MEDIA_LOCATION", "media").strip("/")
AWS_SEED_ASSET_LOCATION = env("AWS_SEED_ASSET_LOCATION", "seed-assets").strip("/")
AWS_PRESIGNED_URL_EXPIRE_SECONDS = int(env("AWS_PRESIGNED_URL_EXPIRE_SECONDS", "900"))
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL") or None
AWS_QUERYSTRING_AUTH = True
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

STORAGES = {
    "default": {
        "BACKEND": "apps.common.storage.S3MediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

APPEND_SLASH = True

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = int(env("EMAIL_TIMEOUT", "10"))
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@theglowmission.com")

CUSTOMER_REGISTRATION_ENABLED = env_bool("CUSTOMER_REGISTRATION_ENABLED", True)
CUSTOMER_PASSWORD_RESET_URL_TEMPLATE = env(
    "CUSTOMER_PASSWORD_RESET_URL_TEMPLATE",
    "https://theglowmission.com/reset-password?uid={uid}&token={token}",
)
CUSTOMER_PASSWORD_RESET_EMAIL_SUBJECT = env("CUSTOMER_PASSWORD_RESET_EMAIL_SUBJECT", "Reset your The Glow Mission password")
CUSTOMER_PASSWORD_RESET_EXPOSE_TOKEN = env_bool("CUSTOMER_PASSWORD_RESET_EXPOSE_TOKEN", DEBUG)
CUSTOMER_NOTIFICATIONS_ENABLED = env_bool("CUSTOMER_NOTIFICATIONS_ENABLED", True)
EXPO_PUSH_ACCESS_TOKEN = env("EXPO_PUSH_ACCESS_TOKEN", "")
WEB_PUSH_PUBLIC_KEY = env("WEB_PUSH_PUBLIC_KEY", "")
WEB_PUSH_PRIVATE_KEY = env("WEB_PUSH_PRIVATE_KEY", "")
WEB_PUSH_SUBJECT = env("WEB_PUSH_SUBJECT", "mailto:info@theglowmission.com")
APP_CONFIG_CACHE_SECONDS = int(env("APP_CONFIG_CACHE_SECONDS", "300"))
FIRST_PARTY_SCHEDULING_ENABLED = env_bool("FIRST_PARTY_SCHEDULING_ENABLED", True)
CALENDLY_BOOKING_FALLBACK_ENABLED = env_bool("CALENDLY_BOOKING_FALLBACK_ENABLED", True)
APPOINTMENT_SLOT_HORIZON_DAYS = int(env("APPOINTMENT_SLOT_HORIZON_DAYS", "60"))
APPOINTMENT_MIN_LEAD_MINUTES = int(env("APPOINTMENT_MIN_LEAD_MINUTES", "240"))
APPOINTMENT_DOWNTIME_MINUTES = int(env("APPOINTMENT_DOWNTIME_MINUTES", "15"))
APPOINTMENT_CUSTOMER_CHANGE_CUTOFF_MINUTES = int(env("APPOINTMENT_CUSTOMER_CHANGE_CUTOFF_MINUTES", "720"))
APPOINTMENT_REMINDER_MINUTES = env_int_list("APPOINTMENT_REMINDER_MINUTES", "1440,120")
APPOINTMENT_SCHEDULER_POLL_SECONDS = int(env("APPOINTMENT_SCHEDULER_POLL_SECONDS", "300"))
GLOW_GST_RATE_PERCENT = env("GLOW_GST_RATE_PERCENT", "18")
