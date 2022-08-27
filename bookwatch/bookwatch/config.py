import sys
import os
import logging



ENV = os.getenv('ENV')
IS_PROD = 'ENV' == 'PROD'
IS_DEV = not IS_PROD

if IS_PROD:
    REDIS_HOST = 'bookwatch_redis'
    LOG_LEVEL = logging.INFO
if IS_DEV:
    REDIS_HOST = '127.0.0.1'
    LOG_LEVEL = logging.DEBUG


root = logging.getLogger()
root.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
