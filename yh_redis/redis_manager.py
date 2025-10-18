from typing import NamedTuple
import redis.asyncio as redis

class RedisConfig(NamedTuple):
    host: str
    port: int
    db: int
    decode_responses: bool
    max_connections: int = 20  # 커넥션풀 최대 연결 수
    retry_on_timeout: bool = True

class RedisManager:
    def __init__(self, config: RedisConfig):
        self.config = config
        self.connectionPool = None
        self.redisClient = None
    
    def _ensure_connection_pool(self):
        """커넥션풀이 없으면 생성"""
        if self.connectionPool is None:
            self.connectionPool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                decode_responses=self.config.decode_responses,
                max_connections=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout
            )
            self.redisClient = redis.Redis(connection_pool=self.connectionPool)
    
    def get_redis_client(self):
        """Redis 클라이언트 반환 (Depends용)"""
        self._ensure_connection_pool()
        return self.redisClient
    
    async def close(self):
        """커넥션풀 종료"""
        if self.connectionPool:
            await self.connectionPool.disconnect()
            self.connectionPool = None
            self.redisClient = None

