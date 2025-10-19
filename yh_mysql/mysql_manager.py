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
    
    async def _ensure_connection_pools(self):
        """커넥션풀들이 없으면 생성"""
        if not self.connection_pool_map:
            for config in self.configList:
                if config.dbNameKey not in self.connection_pool_map:
                    pool = await self.create_connection_pool(config)
                    self.connection_pool_map[config.dbNameKey] = pool
    
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
    
    async def get_connection_pool(self, dbNameKey: str):
        """커넥션풀 반환 (Depends용)"""
        await self._ensure_connection_pools()
        if dbNameKey not in self.connection_pool_map:
            raise KeyError(f"Database connection '{dbNameKey}' not found")
        return self.connection_pool_map[dbNameKey]
    
    async def get_connection(self, dbNameKey: str):
        """커넥션 가져오기"""
        pool = await self.get_connection_pool(dbNameKey)
        return await pool.acquire()
    
    async def close_all_connections(self):
        """모든 커넥션 풀 종료"""
        for pool in self.connection_pool_map.values():
            pool.close()
            await pool.wait_closed()
        self.connection_pool_map.clear()
