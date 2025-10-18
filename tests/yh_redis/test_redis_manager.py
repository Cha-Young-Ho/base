import pytest
from pytest_mock import MockerFixture
from yh_redis import RedisManager, RedisConfig

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
        await redis_manager.initialize()
        assert redis_manager.redisClient is not None
    
    @pytest.mark.asyncio
    async def test_get_redis_client(self, mocker: MockerFixture):
        redis_manager = RedisManager(redis_config)
        mock_connection_client = mocker.Mock()

        mocker.patch("redis.asyncio.Redis", return_value=mock_connection_client)
        await redis_manager.initialize()

        assert await redis_manager.get_redis_client() is not None