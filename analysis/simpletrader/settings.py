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
    'simpletrader.accounts',
    'simpletrader.trade',
    'simpletrader.demo_accounts_matchers',
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
        'HOST': 'analysisdb_pgbouncer',
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

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


ENV = 'PRODUCTION' if not DEBUG else 'DEBUG'


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.tornado import TornadoIntegration
from sentry_sdk.integrations.redis import RedisIntegration


# sentry_sdk.init(
#     dsn="https://4e07479d060c43129263ed0723453527@ibelieve.itshouldbe.fun/2",
#     integrations=[
#         DjangoIntegration(),
#         TornadoIntegration(),
#         RedisIntegration(),
#         CeleryIntegration(),

#     ],
#     environment=ENV,
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0,

#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True
# )


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


CELERY_REDIS_HOST = 'celery_redis'
CELERY_REDIS_PORT = '6379'
CELERY_REDIS_DB_NO = '0'


BOOK_WATCH_REDIS_HOST = 'bookwatch_redis'
BOOK_WATCH_REDIS_PORT = '6379'
BOOK_WATCH_REDIS_DB_NO = '0'


if DEBUG:
    JOURNAL_REDIS_HOST = '127.0.0.1'
    JOURNAL_REDIS_PORT = '6379'
    JOURNAL_REDIS_DB_NO = '0'

    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_DB_NO = '2'

    CELERY_REDIS_HOST = '127.0.0.1'
    CELERY_REDIS_PORT = '6379'
    CELERY_REDIS_DB_NO = '3'

    BOOK_WATCH_REDIS_HOST = '127.0.0.1'
    BOOK_WATCH_REDIS_PORT = '6379'
    BOOK_WATCH_REDIS_DB_NO = '4'


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




CELERY_BROKER = f'redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DB_NO}'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_TASK_ROUTES = {
    'analysis.q.*': {'queue': 'analysis_query'},
    'trade.*': {'queue': 'trade_rpc'},
}
CELERY_TIMEZONE = TIME_ZONE

