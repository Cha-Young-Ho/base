from typing import NamedTuple
import redis.asyncio as redis

class RedisConfig(NamedTuple):
    host: str
    port: int
    db: int
    decode_responses: bool

class RedisManager:
    def __init__(self, config: RedisConfig):
        self.config = config
        self.redisClient = None
    
    async def initialize(self):
        """Redis 비동기 클라이언트 초기화"""
        self.redisClient = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            decode_responses=self.config.decode_responses
        )
    
    async def get_redis_client(self):
        """Redis 클라이언트 반환 (자동 초기화)"""
        if self.redisClient is None:
            await self.initialize()
        return self.redisClient

