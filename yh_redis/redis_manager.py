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
    """
    Redis 연결 관리자 (Fail-Fast 패턴)
    
    - lifespan에서 connect() 호출: 앱 시작 시 연결 확인 (Fail-Fast)
    - get_redis_client(): Depends()에서 사용 (이미 연결된 클라이언트 반환)
    - close(): 앱 종료 시 안전하게 연결 종료
    """
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self.connectionPool = None
        self.redisClient = None
    
    async def connect(self):
        """
        앱 시작 시 호출되는 초기화 메서드 (Fail-Fast)
        
        - 커넥션 풀 생성
        - ping으로 연결 테스트
        - 실패 시 Exception 발생 → 앱 시작 중단
        """
        if self.connectionPool is not None:
            return  # 이미 연결됨
        
        try:
            self.connectionPool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                decode_responses=self.config.decode_responses,
                max_connections=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout
            )
            self.redisClient = redis.Redis(connection_pool=self.connectionPool)
            
            # !! 연결 테스트 (가장 중요) !!
            await self.redisClient.ping()
            print(f"✓ Redis connected: {self.config.host}:{self.config.port}")
            
        except Exception as e:
            # 실패 시 리소스 정리
            await self.close()
            # 에러를 다시 raise해서 lifespan이 중단되도록 함 (Fail-Fast)
            raise Exception(f"FATAL: Failed to connect to Redis: {e}")
    
    def get_redis_client(self) -> redis.Redis:
        """
        Redis 클라이언트 반환 (Depends용)
        
        주의: 여기서 더 이상 풀을 생성하지 않음!
        lifespan에서 이미 connect()가 호출되어야 함.
        """
        if self.redisClient is None:
            raise RuntimeError(
                "Redis client is not available. "
                "Did you call await redis_manager.connect() in lifespan?"
            )
        return self.redisClient
    
    async def close(self):
        """커넥션풀 종료 (앱 종료 시)"""
        if self.redisClient:
            await self.redisClient.close()
        if self.connectionPool:
            await self.connectionPool.disconnect()
        
        self.connectionPool = None
        self.redisClient = None
        print("✓ Redis connection closed")