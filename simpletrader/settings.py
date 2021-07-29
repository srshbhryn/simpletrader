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


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname}\t\t{asctime}\t\t{message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
             # But the emails are plain text by default - HTML is nicer
            'include_html': True,
        },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': CONFIGS.get('LOGFILE','/var/log/simpletrader/django.log'),
            'formatter': 'verbose'

        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
            # 'level': 'INFO',
            'propagate': False,
        },
        # Your own app - this assumes all your logger names start with "myapp."
        'binance': {
            'handlers': ['logfile'],
            # 'level': 'WARNING', # Or maybe INFO or DEBUG
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'propagate': False
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
}

CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_BROKER = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NO}'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = CONFIGS.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_USE_TLS = True
# EMAIL_PORT = CONFIGS.get('EMAIL_PORT', 587)
# EMAIL_HOST_USER = CONFIGS.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = CONFIGS.get('EMAIL_HOST_PASSWORD')


#########  APP settings:
NOBITEX = {
    'DATA_DIR_PATH': BASE_DIR / 'data/nobitex',
    'MARKETS': [
        ('BTC', 'IRT'),
        ('ETH', 'IRT'),
        # ('LTC', 'IRT'),
        # ('XRP', 'IRT'),
        # ('BCH', 'IRT'),
        # ('BNB', 'IRT'),
        # ('EOS', 'IRT'),
        # ('XLM', 'IRT'),
        # ('ETC', 'IRT'),
        # ('TRX', 'IRT'),
        # ('DOGE', 'IRT'),
        # ('UNI', 'IRT'),
        # ('DAI', 'IRT'),
        ('USDT', 'IRT'),
        ('BTC', 'USDT'),
        ('ETH', 'USDT'),
        # ('LTC', 'USDT'),
        # ('XRP', 'USDT'),
        # ('BCH', 'USDT'),
        # ('BNB', 'USDT'),
        # ('EOS', 'USDT'),
        # ('XLM', 'USDT'),
        # ('ETC', 'USDT'),
        # ('TRX', 'USDT'),
        # ('DOGE', 'USDT'),
        # ('UNI', 'USDT'),
        # ('DAI', 'USDT'),
    ],
    'FEES': {
        'TAKER': .0015,
        'MAKER': .0015,
    },
    'JOURNAL_ROTATE_PERIOD': {
        'marketdata_journal': 60,
        'trade_journal': 60*5,
    },
    'TASK_PERIODS': {
        'collect_market_data': 2,
        'collect_market_trades': 30,
        'store_market_data': 300,
        'store_trades': 60*5*5,
    }
}

