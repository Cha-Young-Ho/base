import pytest
from pytest_mock import MockerFixture
from yh_redis.redis_manager import RedisManager, RedisConfig

redis_config = RedisConfig(
    host="test",
    port=6379,
    db=0,
    decode_responses=True,
)

class TestRedisManager:
    def test_redis_manager_init(self):
        redis_manager = RedisManager(redis_config)
        assert redis_manager is not None
        assert redis_manager.config == redis_config
        assert redis_manager.connectionPool is None
        assert redis_manager.redisClient is None
    
    @pytest.mark.asyncio
    async def test_redis_connect_success(self, mocker: MockerFixture):
        redis_manager = RedisManager(redis_config)
        mock_pool = mocker.Mock()
        mock_client = mocker.Mock()
        
        # ping 메서드를 awaitable하게 만들기
        async def mock_ping():
            return True
        mock_client.ping = mock_ping
        
        mocker.patch("redis.asyncio.ConnectionPool", return_value=mock_pool)
        mocker.patch("redis.asyncio.Redis", return_value=mock_client)
        
        await redis_manager.connect()
        
        assert redis_manager.connectionPool == mock_pool
        assert redis_manager.redisClient == mock_client
    
    @pytest.mark.asyncio
    async def test_redis_connect_failure(self, mocker: MockerFixture):
        redis_manager = RedisManager(redis_config)
        mock_pool = mocker.Mock()
        mock_client = mocker.Mock()
        
        # ping이 실패하도록 설정
        async def mock_ping():
            raise Exception("Connection failed")
        mock_client.ping = mock_ping
        
        # close 메서드를 awaitable하게 만들기
        async def mock_close():
            pass
        mock_client.close = mock_close
        
        # disconnect 메서드를 awaitable하게 만들기
        async def mock_disconnect():
            pass
        mock_pool.disconnect = mock_disconnect
        
        mocker.patch("redis.asyncio.ConnectionPool", return_value=mock_pool)
        mocker.patch("redis.asyncio.Redis", return_value=mock_client)
        
        with pytest.raises(Exception, match="FATAL: Failed to connect to Redis"):
            await redis_manager.connect()
        
        # 실패 시 리소스가 정리되었는지 확인
        assert redis_manager.connectionPool is None
        assert redis_manager.redisClient is None
    
    def test_get_redis_client_before_connect(self):
        redis_manager = RedisManager(redis_config)
        
        with pytest.raises(RuntimeError, match="Redis client is not available"):
            redis_manager.get_redis_client()
    
    @pytest.mark.asyncio
    async def test_get_redis_client_after_connect(self, mocker: MockerFixture):
        redis_manager = RedisManager(redis_config)
        mock_pool = mocker.Mock()
        mock_client = mocker.Mock()
        
        async def mock_ping():
            return True
        mock_client.ping = mock_ping
        
        mocker.patch("redis.asyncio.ConnectionPool", return_value=mock_pool)
        mocker.patch("redis.asyncio.Redis", return_value=mock_client)
        
        await redis_manager.connect()
        client = redis_manager.get_redis_client()
        
        assert client == mock_client
    
    @pytest.mark.asyncio
    async def test_close(self, mocker: MockerFixture):
        redis_manager = RedisManager(redis_config)
        mock_pool = mocker.Mock()
        mock_client = mocker.Mock()
        
        async def mock_ping():
            return True
        mock_client.ping = mock_ping
        
        # close 메서드를 awaitable하게 만들기
        async def mock_close():
            pass
        mock_client.close = mock_close
        
        # disconnect 메서드를 awaitable하게 만들기
        async def mock_disconnect():
            pass
        mock_pool.disconnect = mock_disconnect
        
        mocker.patch("redis.asyncio.ConnectionPool", return_value=mock_pool)
        mocker.patch("redis.asyncio.Redis", return_value=mock_client)
        
        await redis_manager.connect()
        await redis_manager.close()
        
        assert redis_manager.connectionPool is None
        assert redis_manager.redisClient is None