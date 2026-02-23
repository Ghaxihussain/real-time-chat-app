from redis.asyncio import Redis
import os

redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)