import pytest
from yh_db import MySQLManager, MySQLConfig
from pytest_mock import MockerFixture

mysql_config = MySQLConfig(
    dbNameKey="test",
    host="localhost",
    port=3306,
    user="root",
    password="rootpassword",
    database="testdb",
)

class TestMySQLManager:
    @pytest.mark.asyncio
    async def test_create_connection_pool(self, mocker: MockerFixture):
        """커넥션 풀 생성 테스트"""
        mock_pool = mocker.Mock()
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        mysql_manager = MySQLManager([mysql_config])
        await mysql_manager.initialize()
        
        assert "test" in mysql_manager.connection_pool_map
        assert mysql_manager.connection_pool_map["test"] == mock_pool

    @pytest.mark.asyncio
    async def test_get_connection(self, mocker: MockerFixture):
        """커넥션 가져오기 테스트"""
        mock_pool = mocker.Mock()
        mock_connection = mocker.Mock()
        
        # acquire 메서드를 awaitable하게 만들기
        async def mock_acquire():
            return mock_connection
        mock_pool.acquire = mock_acquire
        
        # AsyncMock을 awaitable하게 만들기
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        mysql_manager = MySQLManager([mysql_config])
        await mysql_manager.initialize()
        
        connection = await mysql_manager.get_connection("test")
        assert connection == mock_connection

    def test_mysql_config_creation(self):
        """MySQLConfig 생성 테스트"""
        config = MySQLConfig(
            dbNameKey="main",
            host="localhost",
            port=3306,
            user="test",
            password="test",
            database="testdb"
        )
        
        assert config.dbNameKey == "main"
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.user == "test"
        assert config.password == "test"
        assert config.database == "testdb"

    @pytest.mark.asyncio
    async def test_get_connection_key_error(self, mocker: MockerFixture):
        """존재하지 않는 키로 커넥션 요청 시 에러 테스트"""
        mock_pool = mocker.Mock()
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        mysql_manager = MySQLManager([mysql_config])
        await mysql_manager.initialize()
        
        # 존재하지 않는 키로 요청
        with pytest.raises(KeyError, match="Database connection 'nonexistent' not found"):
            await mysql_manager.get_connection("nonexistent")
