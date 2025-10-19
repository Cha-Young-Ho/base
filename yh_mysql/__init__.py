"""
yh_mysql - MySQL Connection Manager with Fail-Fast Pattern

Usage:
    # main.py
    from yh_mysql import mysql_manager, MySQLConfig
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: Connect to MySQL (Fail-Fast)
        configs = [
            MySQLConfig(
                dbNameKey="main",
                host="localhost",
                port=3306,
                user="root",
                password="rootpassword",
                database="myapp"
            )
        ]
        mysql_manager.configList = configs
        await mysql_manager.connect()  # Fail-Fast: 연결 실패 시 앱 시작 중단
        
        yield
        
        # Shutdown: Close MySQL connections
        await mysql_manager.close()
    
    # router.py
    from yh_mysql import mysql_manager, MySQLPool
    from fastapi import Depends
    
    @router.post("/users")
    async def create_user(
        pool: MySQLPool = Depends(mysql_manager.get_connection_pool)
    ):
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                return result
"""

from .mysql_manager import MySQLManager, MySQLConfig
import aiomysql

# 타입 export
MySQLPool = aiomysql.Pool

# 전역 싱글톤 인스턴스 생성 (configList는 lifespan에서 주입)
mysql_manager = MySQLManager(
    configList=[
        MySQLConfig(
            dbNameKey="main",  # 기본값, lifespan에서 덮어쓸 것
            host="localhost",
            port=3306,
            user="root",
            password="rootpassword",
            database="myapp"
        )
    ]
)

__all__ = ['MySQLManager', 'MySQLConfig', 'MySQLPool', 'mysql_manager']