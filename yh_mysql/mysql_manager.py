import aiomysql
from typing import List, NamedTuple

class MySQLConfig(NamedTuple):
    dbNameKey: str
    host: str
    port: int
    user: str
    password: str
    database: str

class MySQLManager:
    """
    MySQL 연결 관리자 (Fail-Fast 패턴)
    
    - lifespan에서 connect() 호출: 앱 시작 시 연결 확인 (Fail-Fast)
    - get_connection_pool(): Depends()에서 사용 (이미 연결된 풀 반환)
    - close(): 앱 종료 시 안전하게 연결 종료
    """
    
    def __init__(self, configList: List[MySQLConfig]):
        self.configList = configList
        self.connection_pool_map = {}
    
    async def connect(self):
        """
        앱 시작 시 호출되는 초기화 메서드 (Fail-Fast)
        
        - 모든 커넥션 풀 생성
        - ping으로 연결 테스트
        - 실패 시 Exception 발생 → 앱 시작 중단
        """
        if self.connection_pool_map:
            return  # 이미 연결됨
        
        try:
            for config in self.configList:
                if config.dbNameKey not in self.connection_pool_map:
                    pool = await self.create_connection_pool(config)
                    self.connection_pool_map[config.dbNameKey] = pool
                    
                    # !! 연결 테스트 (가장 중요) !!
                    async with pool.acquire() as conn:
                        await conn.ping()
                    print(f"✓ MySQL connected: {config.host}:{config.port}/{config.database}")
            
        except Exception as e:
            # 실패 시 리소스 정리
            await self.close()
            # 에러를 다시 raise해서 lifespan이 중단되도록 함 (Fail-Fast)
            raise Exception(f"FATAL: Failed to connect to MySQL: {e}")
    
    async def create_connection_pool(self, config: MySQLConfig):
        return await aiomysql.create_pool(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            db=config.database,
            charset='utf8mb4',
            cursorclass=aiomysql.DictCursor
        )
    
    def get_connection_pool(self, dbNameKey: str):
        """
        커넥션풀 반환 (Depends용)
        
        주의: 여기서 더 이상 풀을 생성하지 않음!
        lifespan에서 이미 connect()가 호출되어야 함.
        """
        if not self.connection_pool_map:
            raise RuntimeError(
                "MySQL connection pools are not available. "
                "Did you call await mysql_manager.connect() in lifespan?"
            )
        
        if dbNameKey not in self.connection_pool_map:
            raise KeyError(f"Database connection '{dbNameKey}' not found")
        
        return self.connection_pool_map[dbNameKey]
    
    async def get_connection(self, dbNameKey: str):
        """커넥션 가져오기"""
        pool = self.get_connection_pool(dbNameKey)
        return await pool.acquire()
    
    async def close(self):
        """모든 커넥션 풀 종료 (앱 종료 시)"""
        for pool in self.connection_pool_map.values():
            pool.close()
            await pool.wait_closed()
        
        self.connection_pool_map.clear()
        print("✓ MySQL connections closed")
