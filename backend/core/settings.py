"""
Django settings for the ecommerce backend.
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def getenv_bool(name: str, default: bool = False) -> bool:
    """Parse boolean-esque environment variables."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = getenv_bool("DJANGO_DEBUG", False)

_allowed_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "*")
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts.split(",") if host.strip()]


INSTALLED_APPS = [
    "jazzmin",  # Must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "taggit",
    "django_quill",
    "accounts",
    "shop",
    "content",
]

MIDDLEWARE = [
    "core.middleware.AdminEnglishMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
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
ASGI_APPLICATION = "core.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "postgres"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "ATOMIC_REQUESTS": True,
    }
}

if getenv_bool("DJANGO_TEST_USE_SQLITE", False):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("DJANGO_SQLITE_DB", BASE_DIR / "test.sqlite3"),
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "ru-ru")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Europe/Moscow")
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("DJANGO_DEFAULT_PAGE_SIZE", "12")),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
}


CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

CORS_ALLOW_ALL_ORIGINS = getenv_bool("DJANGO_CORS_ALLOW_ALL", True)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]

CORS_ALLOW_CREDENTIALS = True


ALGOLIA_APP_ID = os.getenv("ALGOLIA_APP_ID", "")
ALGOLIA_ADMIN_API_KEY = os.getenv("ALGOLIA_ADMIN_API_KEY", "")
ALGOLIA_INDEX_NAME = os.getenv("ALGOLIA_INDEX_NAME", "shop_products")
ALGOLIA_ENABLED = bool(ALGOLIA_APP_ID and ALGOLIA_ADMIN_API_KEY and ALGOLIA_INDEX_NAME)


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "60"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

EMAIL_BACKEND = os.getenv(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_DEFAULT_FROM_EMAIL", "no-reply@example.com")
EMAIL_HOST = os.getenv("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("DJANGO_EMAIL_PORT", "587")) if EMAIL_HOST else None
EMAIL_HOST_USER = os.getenv("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = getenv_bool("DJANGO_EMAIL_USE_TLS", True)
FRONTEND_PASSWORD_RESET_URL = os.getenv(
    "FRONTEND_PASSWORD_RESET_URL", "http://localhost:3000/reset-password"
)

# Jazzmin configuration
JAZZMIN_SETTINGS = {
    "site_title": "Shopster Admin",
    "site_header": "Shopster Admin",
    "site_brand": "Shopster",
    "welcome_sign": "Welcome to Shopster Admin",
    "copyright": "Shopster",
    # Layout & navigation
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "shop",
        "auth",
        "content",
        "taggit",
    ],
    # Top menu entries
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"app": "shop", "name": "Catalog"},
        {"model": "auth.User", "name": "Users"},
        {"name": "Site", "url": "/", "new_window": True},
    ],
    # Per-app/model icons
    "icons": {
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "shop": "fas fa-store",
        "shop.category": "fas fa-layer-group",
        "shop.product": "fas fa-box",
        "shop.productimage": "far fa-image",
        "shop.cart": "fas fa-shopping-cart",
        "shop.cartitem": "fas fa-list",
        "shop.order": "fas fa-receipt",
        "shop.orderitem": "fas fa-list-ul",
        "shop.productreview": "fas fa-star",
        "content": "fas fa-file-alt",
    },
    # Change form layout and related modals
    "related_modal_active": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_Overrides": {
        "shop.product": "collapsible",
        "shop.order": "horizontal_tabs",
    },
    # Useful quick links in user menu
    "usermenu_links": [
        {"name": "View site", "url": "/", "icon": "fas fa-globe", "new_window": True},
        {"model": "auth.user"},
    ],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "minty",  # stronger visual difference
    "dark_mode_theme": "darkly",
    "navbar": "navbar-primary",
    "footer_fixed": True,
    "actions_sticky_top": True,
    "body_small_text": False,
    "brand_colour": "navbar-primary",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "danger": "btn-danger",
        "info": "btn-info",
    },
}
