from redis.asyncio import Redis
from bookwatch import settings

redis = Redis(
    host=settings.REDIS_HOST,
    db=settings.REDIS_DB,
)
