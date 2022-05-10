import os, json
from pathlib import Path

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
    'timescale',
    'simpletrader.base',
    #
    'simpletrader.nobitex',
    'simpletrader.kucoin',
    'simpletrader.indices',
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
        'NAME': CONFIGS.get('DEFAULT_DB_NAME', 'simpletrader_default'),
        'USER': CONFIGS.get('DEFAULT_DB_USER', 'simpletrader_default'),
        'PASSWORD': CONFIGS.get('DEFAULT_DB_PASSWORD'),
        'HOST': CONFIGS.get('DEFAULT_DB_HOST', '127.0.0.1'),
        'PORT': CONFIGS.get('DEFAULT_DB_PORT', '5432'),
    },
    'timescale': {
        'ENGINE': 'timescale.db.backends.postgresql',
        'NAME': CONFIGS.get('TIMESCALE_DB_NAME', 'simpletrader_ts'),
        'USER': CONFIGS.get('TIMESCALE_DB_USER', 'simpletrader_ts'),
        'PASSWORD': CONFIGS.get('TIMESCALE_DB_PASSWORD'),
        'HOST': CONFIGS.get('TIMESCALE_DB_HOST', '127.0.0.1'),
        'PORT': CONFIGS.get('TIMESCALE_DB_PORT', '5432'),
    }
}
DB_ROUTING = {
    'timescale': [
        'simpletrader.nobitex',
        'simpletrader.kucoin_data',
        'simpletrader.kucoin_index',
    ],
}
DEFAULT_DB = 'default'
DATABASE_ROUTERS = ['simpletrader.db_router.Router',]

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
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': CONFIGS.get('LOGDIR','/var/log/simpletrader/simpletrader.log'),
            'formatter': 'verbose'
        },
        'logfile_q': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': CONFIGS.get('LOGDIR','/var/log/simpletrader/simpletrader_q.log'),
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
            'handlers': ['logfile'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['logfile_q'],
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
STATIC_ROOT = CONFIGS.get('STATIC_ROOT', '/srv/www/simpletrader/static/')

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
    'index_manager': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}',
        'TIMEOUT': None,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PICKLE_VERSION': 4,
        },
    },
}


CELERY_BROKER = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_RESULT_BACKEND = 'django-db'
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
# EMAIL_HOST = CONFIGS.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_USE_TLS = True
# EMAIL_PORT = CONFIGS.get('EMAIL_PORT', 587)
# EMAIL_HOST_USER = CONFIGS.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = CONFIGS.get('EMAIL_HOST_PASSWORD')


#########  APP settings:
### base:
JOURNALS = {
    'DATA_DIR': BASE_DIR / 'data/journals/'
}
