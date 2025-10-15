import aiomysql
from typing import List

class MySQLConfig:
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
        return await self.connection_pool_map[dbNameKey].acquire()