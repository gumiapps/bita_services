import os
from pathlib import Path
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-#$v_sv39h&bcr3cs(urra+ff97$u*l6!bw=fciz@8$xlppyu5b"

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "inventory",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

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

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "inventory"),
        "USER": os.environ.get("DB_USER", "inventory_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "testpass123"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "inventory.authentication.RemoteJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Inventory service API",
    "DESCRIPTION": "Inventory Management API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

ITEM_LIST_QUERY_PARAMETERS = [
    OpenApiParameter(
        name="category_id",
        description="Filter by category ID",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="manufacturer_id",
        description="Filter by manufacturer ID",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="visible",
        description="Filter by visibility (true/false)",
        required=False,
        type=OpenApiTypes.BOOL,
    ),
    OpenApiParameter(
        name="returnable",
        description="Filter by returnable (true/false)",
        required=False,
        type=OpenApiTypes.BOOL,
    ),
    OpenApiParameter(
        name="search",
        description="Search term",
        required=False,
        type=OpenApiTypes.STR,
    ),
]

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")
