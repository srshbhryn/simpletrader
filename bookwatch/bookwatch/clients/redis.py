from redis.asyncio import Redis
from bookwatch import config
from bookwatch.markets import Asset, Exchange


redis = Redis(
    host=config.REDIS_HOST,
)
