import pytest
from yh_mysql.mysql_manager import MySQLManager, MySQLConfig
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
    def test_mysql_manager_init(self):
        """MySQLManager 초기화 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        assert mysql_manager is not None
        assert mysql_manager.configList == [mysql_config]
        assert mysql_manager.connection_pool_map == {}
    
    @pytest.mark.asyncio
    async def test_mysql_connect_success(self, mocker: MockerFixture):
        """MySQL 연결 성공 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        mock_pool = mocker.Mock()
        mock_connection = mocker.Mock()
        
        # ping 메서드를 awaitable하게 만들기
        async def mock_ping():
            return True
        mock_connection.ping = mock_ping
        
        # acquire를 async context manager로 만들기
        class MockAcquireContext:
            def __init__(self, connection):
                self.connection = connection
            
            async def __aenter__(self):
                return self.connection
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        def mock_acquire():
            return MockAcquireContext(mock_connection)
        mock_pool.acquire = mock_acquire
        
        # wait_closed 메서드를 awaitable하게 만들기
        async def mock_wait_closed():
            pass
        mock_pool.wait_closed = mock_wait_closed
        
        # create_pool을 awaitable하게 만들기
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        await mysql_manager.connect()
        
        assert "test" in mysql_manager.connection_pool_map
        assert mysql_manager.connection_pool_map["test"] == mock_pool
    
    @pytest.mark.asyncio
    async def test_mysql_connect_failure(self, mocker: MockerFixture):
        """MySQL 연결 실패 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        mock_pool = mocker.Mock()
        mock_connection = mocker.Mock()
        
        # ping이 실패하도록 설정
        async def mock_ping():
            raise Exception("Connection failed")
        mock_connection.ping = mock_ping
        
        # acquire를 async context manager로 만들기
        class MockAcquireContext:
            def __init__(self, connection):
                self.connection = connection
            
            async def __aenter__(self):
                return self.connection
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        def mock_acquire():
            return MockAcquireContext(mock_connection)
        mock_pool.acquire = mock_acquire
        
        # wait_closed 메서드를 awaitable하게 만들기
        async def mock_wait_closed():
            pass
        mock_pool.wait_closed = mock_wait_closed
        
        # create_pool을 awaitable하게 만들기
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        with pytest.raises(Exception, match="FATAL: Failed to connect to MySQL"):
            await mysql_manager.connect()
        
        # 실패 시 리소스가 정리되었는지 확인
        assert mysql_manager.connection_pool_map == {}
    
    def test_get_connection_pool_before_connect(self):
        """연결 전에 커넥션 풀 요청 시 에러 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        
        with pytest.raises(RuntimeError, match="MySQL connection pools are not available"):
            mysql_manager.get_connection_pool("test")
    
    @pytest.mark.asyncio
    async def test_get_connection_pool_after_connect(self, mocker: MockerFixture):
        """연결 후 커넥션 풀 요청 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        mock_pool = mocker.Mock()
        mock_connection = mocker.Mock()
        
        async def mock_ping():
            return True
        mock_connection.ping = mock_ping
        
        # acquire를 async context manager로 만들기
        class MockAcquireContext:
            def __init__(self, connection):
                self.connection = connection
            
            async def __aenter__(self):
                return self.connection
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        def mock_acquire():
            return MockAcquireContext(mock_connection)
        mock_pool.acquire = mock_acquire
        
        async def mock_wait_closed():
            pass
        mock_pool.wait_closed = mock_wait_closed
        
        # create_pool을 awaitable하게 만들기
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        await mysql_manager.connect()
        pool = mysql_manager.get_connection_pool("test")
        
        assert pool == mock_pool
    
    @pytest.mark.asyncio
    async def test_get_connection_key_error(self, mocker: MockerFixture):
        """존재하지 않는 키로 커넥션 요청 시 에러 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        mock_pool = mocker.Mock()
        mock_connection = mocker.Mock()
        
        async def mock_ping():
            return True
        mock_connection.ping = mock_ping
        
        # acquire를 async context manager로 만들기
        class MockAcquireContext:
            def __init__(self, connection):
                self.connection = connection
            
            async def __aenter__(self):
                return self.connection
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        def mock_acquire():
            return MockAcquireContext(mock_connection)
        mock_pool.acquire = mock_acquire
        
        async def mock_wait_closed():
            pass
        mock_pool.wait_closed = mock_wait_closed
        
        # create_pool을 awaitable하게 만들기
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        await mysql_manager.connect()
        
        # 존재하지 않는 키로 요청
        with pytest.raises(KeyError, match="Database connection 'nonexistent' not found"):
            mysql_manager.get_connection_pool("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_connection(self, mocker: MockerFixture):
        """커넥션 가져오기 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        mock_pool = mocker.Mock()
        mock_connection = mocker.Mock()
        
        async def mock_ping():
            return True
        mock_connection.ping = mock_ping
        
        # acquire를 async context manager로 만들기 (connect용)
        class MockAcquireContext:
            def __init__(self, connection):
                self.connection = connection
            
            async def __aenter__(self):
                return self.connection
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        # acquire를 awaitable하게 만들기 (get_connection용)
        async def mock_acquire():
            return mock_connection
        
        # connect에서는 context manager, get_connection에서는 awaitable
        def mock_acquire_factory():
            return MockAcquireContext(mock_connection)
        mock_pool.acquire = mock_acquire_factory
        
        # get_connection에서 사용할 별도 acquire 메서드
        mock_pool.acquire_direct = mock_acquire
        
        async def mock_wait_closed():
            pass
        mock_pool.wait_closed = mock_wait_closed
        
        # create_pool을 awaitable하게 만들기
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        await mysql_manager.connect()
        
        # get_connection에서 사용할 acquire를 직접 mock
        mocker.patch.object(mock_pool, 'acquire', side_effect=mock_acquire)
        
        connection = await mysql_manager.get_connection("test")
        
        assert connection == mock_connection
    
    @pytest.mark.asyncio
    async def test_close(self, mocker: MockerFixture):
        """연결 종료 테스트"""
        mysql_manager = MySQLManager([mysql_config])
        mock_pool = mocker.Mock()
        mock_connection = mocker.Mock()
        
        async def mock_ping():
            return True
        mock_connection.ping = mock_ping
        
        # acquire를 async context manager로 만들기
        class MockAcquireContext:
            def __init__(self, connection):
                self.connection = connection
            
            async def __aenter__(self):
                return self.connection
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        def mock_acquire():
            return MockAcquireContext(mock_connection)
        mock_pool.acquire = mock_acquire
        
        async def mock_wait_closed():
            pass
        mock_pool.wait_closed = mock_wait_closed
        
        # create_pool을 awaitable하게 만들기
        async def mock_create_pool(*args, **kwargs):
            return mock_pool
        mocker.patch("aiomysql.create_pool", side_effect=mock_create_pool)
        
        await mysql_manager.connect()
        await mysql_manager.close()
        
        assert mysql_manager.connection_pool_map == {}
    
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
