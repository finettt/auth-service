from premier.asgi import ASGIGateway, GatewayConfig
from premier.providers.redis import AsyncRedisCache
from redis.asyncio import Redis
from src.app import app
from src.database.settings import settings


redis_client = Redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
cache_provider = AsyncRedisCache(redis_client)

config = GatewayConfig.from_file("premier.yml")
gateway = ASGIGateway(config=config, app=app, cache_provider=cache_provider)
