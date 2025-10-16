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
    def __init__(self, configList: List[MySQLConfig]):
        self.configList = configList
        self.connection_pool_map = {}
    
    async def initialize(self):
        """명시적으로 초기화"""
        for config in self.configList:
            self.connection_pool_map[config.dbNameKey] = await self.create_connection_pool(config)
    
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
    
    async def get_connection(self, dbNameKey: str):
        """커넥션 가져오기"""
        if dbNameKey not in self.connection_pool_map:
            raise KeyError(f"Database connection '{dbNameKey}' not found")
        return await self.connection_pool_map[dbNameKey].acquire()
    
    async def close_all_connections(self):
        """모든 커넥션 풀 종료"""
        for pool in self.connection_pool_map.values():
            pool.close()
            await pool.wait_closed()
        self.connection_pool_map.clear()
