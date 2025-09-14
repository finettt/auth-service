import redis
from src.database.settings import settings


def get_redis_connection():
    """Get a Redis connection."""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )


def close_redis_connection(redis_conn):
    """Close a Redis connection."""
    if redis_conn:
        redis_conn.close()