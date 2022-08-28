import os

ENV = os.getenv('ENV')
IS_PROD = ENV == 'PROD'
IS_DEV = not IS_PROD

if IS_PROD:
    REDIS_HOST = 'bookwatch_redis'
if IS_DEV:
    REDIS_HOST = '127.0.0.1'
