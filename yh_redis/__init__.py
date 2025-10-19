"""
yh_redis - Redis Connection Manager with Fail-Fast Pattern

Usage:
    # main.py
    from yh_redis import redis_manager, RedisConfig
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: Connect to Redis (Fail-Fast)
        config = RedisConfig(host="localhost", port=6379, db=0, decode_responses=True)
        redis_manager.config = config
        await redis_manager.connect()  # Fail-Fast: 연결 실패 시 앱 시작 중단
        
        yield
        
        # Shutdown: Close Redis connection
        await redis_manager.close()
    
    # router.py
    from yh_redis import redis_manager, RedisClient
    from fastapi import Depends
    
    @router.post("/login")
    async def login(
        redis_client: RedisClient = Depends(redis_manager.get_redis_client)
    ):
        await redis_client.ping()
"""

from .redis_manager import RedisManager, RedisConfig
import redis.asyncio as redis

# 타입 export
RedisClient = redis.Redis

# 전역 싱글톤 인스턴스 생성 (config는 lifespan에서 주입)
redis_manager = RedisManager(
    config=RedisConfig(
        host="localhost",  # 기본값, lifespan에서 덮어쓸 것
        port=6379,
        db=0,
        decode_responses=True
    )
)

__all__ = ['RedisManager', 'RedisConfig', 'RedisClient', 'redis_manager']