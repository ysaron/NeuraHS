from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(filename='.env.dev'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Импорт разделенных настроек
try:
    from .local_settings import *   # В продакшне файл отсутствует --> загрузится файл продакшн-настроек
except ImportError:
    from .prod_settings import *

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gallery.apps.GalleryConfig',
    'accounts.apps.AccountsConfig',
    'utils.apps.UtilsConfig',
    'core.apps.CoreConfig',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',    # включение/отключение Debug Toolbar здесь
]

ROOT_URLCONF = 'neura_hs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # доп. папки в путях поиска шаблонов
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

WSGI_APPLICATION = 'neura_hs.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'nhs_cache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройка пути к медиафайлам
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Выбор в админ-панели множества записей
DATA_UPLOAD_MAX_NUMBER_FIELDS = 13000

# Перенаправить на домашний URL после входа в систему
# (по умолчанию перенаправляет на /accounts/profile/)
LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = 'accounts/signin/'

# Настройки email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'   # SMTP-сервер исходящей почты
EMAIL_PORT = 465    # 465 (SSL) или 587 (TLS)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')

# --------------------------------------------- НАСТРОЙКИ ПРОЕКТА --------------------------------------------------- #

TOP_MENU = {
    'main': {'title': "Главная", 'url_name': 'home'},
    'about': {'title': "О сайте", 'url_name': 'about'},
    'contact': {'title': "Обратная связь", 'url_name': 'contact'}
}

SIDE_MENU = {
    'main': {'title': "Галерея", 'url_name': 'gallery:index', 'popup': ''},
    'base': {'title': "База картонок",
             'real': {'title': "Hearthstone", 'url_name': 'gallery:realcards', 'popup': ''},
             'fan': {'title': "Фан-карты", 'url_name': 'gallery:fancards', 'popup': 'Карты, созданные пользователями'},
             'neura': {'title': "Нейрокартонки", 'url_name': 'gallery:index', 'popup': 'В планах'}},
    'create': {'title': "Создать карту", 'url_name': 'gallery:createcard', 'popup': 'Создание фан-карты'},
    'authors': {'title': "Авторы фан-карт", 'url_name': 'gallery:authors', 'popup': ''}
}

# API Hearthstone
HSAPI_BASEURL = os.environ.get('HSAPI_BASEURL')
HSAPI_HOST = os.environ.get('HSAPI_HOST')
X_RAPIDARI_KEY = os.environ.get('X_RAPIDARI_KEY')
