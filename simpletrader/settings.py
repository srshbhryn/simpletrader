import os, json
from pathlib import Path, WindowsPath

BASE_DIR = Path(__file__).resolve().parent.parent

with open(os.getenv('CONFPATH', '/etc/simpletrader/conf.json'), 'r') as f:
    CONFIGS = json.load(f)

SECRET_KEY = CONFIGS.get('SECRET_KEY', 'asfiug23bi2u3bg23')
DEBUG = CONFIGS.get('DEBUG', False)

ALLOWED_HOSTS = ['*'] if DEBUG else CONFIGS.get('ALLOWED_HOSTS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
    'django_celery_results',
    'django_celery_beat',
    #
    'nobitex',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if DEBUG:
    MIDDLEWARE += [
        'django_sqlprint_middleware.SqlPrintMiddleware',
    ]

ROOT_URLCONF = 'simpletrader.urls'

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

WSGI_APPLICATION = 'simpletrader.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': CONFIGS.get('DB_NAME', 'simpletrader'),
        'USER': CONFIGS.get('DB_USER', 'simpletrader'),
        'PASSWORD': CONFIGS.get('DB_PASSWORD'),
        'HOST': CONFIGS.get('DB_HOST', '127.0.0.1'),
        'PORT': CONFIGS.get('DB_PORT', '3306'),
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST = CONFIGS.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = CONFIGS.get('REDIS_PORT', '6379')
REDIS_DB_NO = CONFIGS.get('REDIS_DB_NO', '10')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}',
        'TIMEOUT': None,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PICKLE_VERSION': 4,
        },
    },
}

CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_BROKER = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
