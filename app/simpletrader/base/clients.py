import redis
import redis.asyncio as async_redis
from django.conf import settings


def get_redis():
    return redis.Redis(
        host=settings.JOURNAL_REDIS_HOST,
        port=int(settings.JOURNAL_REDIS_PORT),
        db=int(settings.JOURNAL_REDIS_DB_NO),
    )

def get_async_redis():
    return async_redis.Redis(
        host=settings.JOURNAL_REDIS_HOST,
        port=int(settings.JOURNAL_REDIS_PORT),
        db=int(settings.JOURNAL_REDIS_DB_NO),
    )
