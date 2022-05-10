import redis
from django.conf import settings


def get_redis_clients():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=int(settings.REDIS_PORT),
        db=int(settings.REDIS_DB_NO),
    )
