import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'asfiug23bi2u3bg23')
DEBUG = os.getenv('DEBUG', '0') == '1'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
    'django_celery_results',
    #
    'timescale',
    'simpletrader.base',
    #
    'simpletrader.nobitex',
    'simpletrader.kucoin',
    # 'simpletrader.indices',
    'simpletrader.trader',
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
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'simpletrader_default',
        'USER': 'simpletrader_default',
        'PASSWORD': 'simpletrader_default',
        'HOST': 'default_db',
        'PORT': '5432',
    },
    'timescale': {
        'ENGINE': 'timescale.db.backends.postgresql',
        'NAME': 'simpletrader_ts',
        'USER': 'simpletrader_ts',
        'PASSWORD': 'simpletrader_ts',
        'HOST': 'timescale_db',
        'PORT': '5432',
    },
    'traderdb': {
        'ENGINE': 'timescale.db.backends.postgresql',
        'NAME': 'traderdb',
        'USER': 'traderdb',
        'PASSWORD': 'traderdb',
        'HOST': 'traderdb',
        'PORT': '5432',
    },
}
if DEBUG:
    for db in DATABASES:
        DATABASES[db] = {
            'ENGINE': 'timescale.db.backends.postgresql',
            'NAME': 'simpletrader_ts',
            'USER': 'simpletrader_ts',
            'PASSWORD': 'simpletrader_ts',
            'HOST': '127.0.0.1',
            'PORT': '5433',
        }

DB_ROUTING = {
    'timescale': [
        'nobitex',
        'kucoin',
        'indices',
    ],
    'traderdb': [
        'trader',
    ]
}
DEFAULT_DB = 'default'
DATABASE_ROUTERS = ['simpletrader.db_router.Router',]


LOGDIR = os.getenv('LOGDIR','/var/log/simpletrader/')
if not LOGDIR[-1] == '/':
    LOGDIR += '/'

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
            'filename': LOGDIR + 'simpletrader.log',
            'formatter': 'verbose'
        },
        'logfile_q': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOGDIR + 'simpletrader_q.log',
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

CELERY_REDIS_HOST = 'celery_redis'
CELERY_REDIS_PORT = '6379'
CELERY_REDIS_DB_NO = '0'

CACHE_REDIS_HOST = 'cache_redis'
CACHE_REDIS_PORT = '6379'
CACHE_REDIS_DB_NO = '0'

if DEBUG:
    JOURNAL_REDIS_HOST = '127.0.0.1'
    JOURNAL_REDIS_PORT = '6379'
    JOURNAL_REDIS_DB_NO = '0'

    CELERY_REDIS_HOST = '127.0.0.1'
    CELERY_REDIS_PORT = '6379'
    CELERY_REDIS_DB_NO = '1'

    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_DB_NO = '2'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{CACHE_REDIS_HOST}:{CACHE_REDIS_PORT}/{CACHE_REDIS_DB_NO}',
        'TIMEOUT': None,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PICKLE_VERSION': 4,
        },
    },
    'index_manager': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{CACHE_REDIS_HOST}:{CACHE_REDIS_PORT}/10',
        'TIMEOUT': None,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PICKLE_VERSION': 4,
        },
    },
}


CELERY_BROKER = f'redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DB_NO}'
CELERY_BROKER_URL = f'redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DB_NO}'
CELERY_RESULT_BACKEND = f'redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DB_NO}'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_TASK_ROUTES = {
    'nobitex.collect.*': {'queue': 'api_call'},
    'nobitex.store.*': {'queue': 'db_insert'},
    'kucoin_data.collect.*': {'queue': 'api_call'},
    'kucoin_data.store.*': {'queue': 'db_insert'},
    'kucoin_index.manage.*': {'queue': 'idx_man'},
    'kucoin_index.hp_compute.*': {'queue': 'idx_hp'},
    'kucoin_index.lp_compute.*': {'queue': 'idx_lp'},
}


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_USE_TLS = True
# EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
