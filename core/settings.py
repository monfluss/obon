import os
import dj_database_url

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#pk35s(&^l5k(h!hq+d%sl+!z8w#y4%a&glt94#-p=5s7td=ys'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# ── Приложения ────────────────────────────────────────────────────
# jazzmin ОБЯЗАН стоять первым — до django.contrib.admin

INSTALLED_APPS = [
    'jazzmin',                          # ← современная тема админки
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'streaming',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# ── База данных ───────────────────────────────────────────────────

DATABASES = {
   'default': dj_database_url.config(
            default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
            conn_max_age=600
        )
}


# ── Валидация паролей ─────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── Локализация ───────────────────────────────────────────────────

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE     = 'Asia/Bishkek'
USE_I18N      = True
USE_TZ        = True


# ── Статика и медиа ───────────────────────────────────────────────

STATIC_URL = '/static/'

MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ── Авторизация ───────────────────────────────────────────────────

LOGIN_REDIRECT_URL  = 'index'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL           = 'login'


# ══════════════════════════════════════════════════════════════════
# JAZZMIN — настройка современной темы админки
# ══════════════════════════════════════════════════════════════════

JAZZMIN_SETTINGS = {
    # ── Основное ──────────────────────────────────────────────────
    "site_title":    "OBON Admin",
    "site_header":   "OBON",
    "site_brand":    "🎵 OBON",
    "site_logo":     None,
    "welcome_sign":  "Панель управления OBON",
    "copyright":     "OBON Music",

    # Глобальный поиск по трекам и заявкам
    "search_model": ["streaming.Track", "streaming.TrackSubmission"],

    # ── Иконки разделов (FontAwesome 5) ───────────────────────────
    "icons": {
        "auth":                      "fas fa-users-cog",
        "auth.user":                 "fas fa-user",
        "auth.group":                "fas fa-users",
        "streaming.track":           "fas fa-music",
        "streaming.artistproxy":     "fas fa-microphone-alt",
        "streaming.genre":           "fas fa-layer-group",
        "streaming.playlist":        "fas fa-list",
        "streaming.tracksubmission": "fas fa-inbox",
    },

    # ── Порядок разделов в сайдбаре ───────────────────────────────
    "order_with_respect_to": [
        "streaming",
        "streaming.tracksubmission",
        "streaming.track",
        "streaming.artistproxy",
        "streaming.genre",
        "streaming.playlist",
        "auth",
    ],

    # ── Верхнее меню ──────────────────────────────────────────────
    "topmenu_links": [
        {
            "name":       "На сайт",
            "url":        "/",
            "new_window": True,
            "icon":       "fas fa-external-link-alt",
        },
        {
            "name": "Новые заявки",
            "url":  "/admin/streaming/tracksubmission/?status__exact=pending",
            "icon": "fas fa-inbox",
        },
        {
            "name": "Добавить трек",
            "url":  "/admin/streaming/track/add/",
            "icon": "fas fa-plus",
        },
    ],

    # ── Быстрые действия на главной админки ───────────────────────
    "custom_links": {
        "streaming": [
            {
                "name":        "Добавить трек",
                "url":         "admin:streaming_track_add",
                "icon":        "fas fa-plus-circle",
                "permissions": ["streaming.add_track"],
            },
            {
                "name":        "Заявки на модерацию",
                "url":         "admin:streaming_tracksubmission_changelist",
                "icon":        "fas fa-inbox",
                "permissions": ["streaming.view_tracksubmission"],
            },
        ]
    },

    # ── Прочее ────────────────────────────────────────────────────
    "show_ui_builder":      False,
    "changeform_format":    "horizontal_tabs",
    "related_modal_active": True,
    "language_chooser":     False,
}


# ── Внешний вид Jazzmin ───────────────────────────────────────────

JAZZMIN_UI_TWEAKS = {
    # Тёмная тема — ближе к стилю OBON
    "theme":                    "darkly",
    "dark_mode_theme":          "darkly",

    # Зелёный акцент как на сайте (#1DB954)
    "accent":                   "accent-success",

    # Navbar
    "navbar":                   "navbar-dark",
    "navbar_fixed":             True,
    "no_navbar_border":         True,
    "brand_colour":             "navbar-success",

    # Sidebar
    "sidebar":                  "sidebar-dark-success",
    "sidebar_fixed":            True,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style":False,
    "sidebar_nav_flat_style":   False,
    "sidebar_nav_legacy_style": False,
    "sidebar_disable_expand":   False,

    # Текст
    "navbar_small_text":        False,
    "footer_small_text":        True,
    "body_small_text":          False,
    "brand_small_text":         False,

    # Прочее
    "layout_boxed":             False,
    "footer_fixed":             False,

    # Цвета кнопок
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-secondary",
        "info":      "btn-outline-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
 }

STATIC_URL = '/static/',
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles'),
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'