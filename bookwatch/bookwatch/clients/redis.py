from redis.asyncio import Redis
from bookwatch import config

redis = Redis(
    host=config.REDIS_HOST,
)
