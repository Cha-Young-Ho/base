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
    
    @pytest.mark.asyncio
    async def test_redis_initialize(self, mocker: MockerFixture):
        redis_manager = RedisManager(redis_config)
        mock_connection_client = mocker.Mock()

        mocker.patch("redis.asyncio.Redis", return_value=mock_connection_client)
        # initialize() 제거 - get_redis_client()에서 자동으로 처리됨
        client = redis_manager.get_redis_client()
        assert client is not None
    
    @pytest.mark.asyncio
    async def test_get_redis_client(self, mocker: MockerFixture):
        redis_manager = RedisManager(redis_config)
        mock_connection_client = mocker.Mock()

        mocker.patch("redis.asyncio.Redis", return_value=mock_connection_client)
        # initialize() 제거 - get_redis_client()에서 자동으로 처리됨

        client = redis_manager.get_redis_client()
        assert client is not None