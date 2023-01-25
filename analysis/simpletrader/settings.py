import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'asfiug23bi2u3bg23')
DEBUG = os.getenv('DEBUG', '0') == '1'


ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'timescale',
    'simpletrader.base',
    'simpletrader.analysis',
]



MIDDLEWARE = []

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
        'ENGINE': 'timescale.db.backends.postgresql',
        'NAME': 'analysisdb',
        'USER': 'analysisdb',
        'PASSWORD': 'analysisdb',
        'HOST': 'analysisdb',
        'PORT': '5432',
        'CONN_MAX_AGE': 3600,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    },
}

if DEBUG:
    DATABASES['default'].update({
        'HOST': '127.0.0.1',
        'PORT': '5436',
    })


LOG_NAME = 'analysis'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime}\t{levelname}\t{name}\t{filename}\t{module}\t{funcName}\t{message}',
            'style': '{',
        },
        'simple': {
            'format': '{asctime}\t{levelname}\t{message}',
            'style': '{',
        },
    },
    'handlers': {
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'include_html': True,
        },
        'console':{
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': f'/tmp/{LOG_NAME}.log',
            'formatter': 'verbose'
        },
        'logfile_q': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': f'/tmp/{LOG_NAME}_q.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'] if not DEBUG else ['logfile'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'] if not DEBUG else ['logfile_q'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'propagate': False,
        },
    },
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
STATIC_ROOT = os.getenv('STATIC_ROOT', '/srv/www/simpletrader/static/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JOURNAL_REDIS_HOST = 'journal_redis'
JOURNAL_REDIS_PORT = '6379'
JOURNAL_REDIS_DB_NO = '0'

CACHE_REDIS_HOST = 'cache_redis'
CACHE_REDIS_PORT = '6379'
CACHE_REDIS_DB_NO = '0'


if DEBUG:
    JOURNAL_REDIS_HOST = '127.0.0.1'
    JOURNAL_REDIS_PORT = '6379'
    JOURNAL_REDIS_DB_NO = '0'

    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_DB_NO = '2'

CACHE_REDIS = f'redis://{CACHE_REDIS_HOST}:{CACHE_REDIS_PORT}/{CACHE_REDIS_DB_NO}'
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_REDIS,
        'TIMEOUT': None,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PICKLE_VERSION': 4,
        },
    },
}