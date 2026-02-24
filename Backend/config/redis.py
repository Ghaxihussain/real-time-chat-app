from redis.asyncio import Redis
import os

redis = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"), decode_responses=True)