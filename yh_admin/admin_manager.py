"""
yh-admin: 자동 CRUD API 및 관리자 페이지 생성 패키지
"""

import os
import asyncio
from dataclasses import dataclass, fields
from typing import Type, List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

class AdminManager:
    """데이터 클래스 기반 자동 CRUD 및 관리자 페이지 생성"""
    
    def __init__(self, mysql_manager, redis_manager=None, auth_manager=None):
        self.mysql_manager = mysql_manager
        self.redis_manager = redis_manager
        self.auth_manager = auth_manager
        self.registered_models = {}  # {model_name: model_class}
        
        # 템플릿 및 정적 파일 설정
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        
        self.templates = Jinja2Templates(directory=template_dir)
        self.static_dir = static_dir
    
    def register_model(self, model_class: Type):
        """데이터 클래스 등록"""
        model_name = model_class.__name__.lower()
        self.registered_models[model_name] = model_class
    
    async def _create_table_if_not_exists(self, model_class):
        """데이터 클래스 기반으로 테이블 자동 생성"""
        table_name = model_class.__name__.lower()
        fields_info = fields(model_class)
        
        # SQL 타입 매핑
        type_mapping = {
            int: "INT AUTO_INCREMENT PRIMARY KEY",
            str: "VARCHAR(255)",
            float: "DECIMAL(10,2)",
            bool: "BOOLEAN",
            Optional[int]: "INT",
            Optional[str]: "VARCHAR(255)",
            Optional[float]: "DECIMAL(10,2)",
            Optional[bool]: "BOOLEAN"
        }
        
        columns = []
        for field in fields_info:
            field_type = self._get_sql_type(field.type, type_mapping)
            nullable = "NULL" if "Optional" in str(field.type) else "NOT NULL"
            
            if field.name == "id" and field.type == int:
                columns.append(f"id INT AUTO_INCREMENT PRIMARY KEY")
            else:
                columns.append(f"{field.name} {field_type} {nullable}")
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        
        try:
            pool = await self.mysql_manager.get_connection_pool("main")
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(create_sql)
                    await conn.commit()
        except Exception as e:
            print(f"테이블 생성 실패 {table_name}: {e}")
    
    def _get_sql_type(self, field_type, type_mapping):
        """필드 타입을 SQL 타입으로 변환"""
        type_str = str(field_type)
        
        if "Optional" in type_str:
            # Optional[Type]에서 Type 추출
            inner_type = type_str.split("[")[1].split("]")[0]
            if inner_type == "<class 'int'>":
                return "INT"
            elif inner_type == "<class 'str'>":
                return "VARCHAR(255)"
            elif inner_type == "<class 'float'>":
                return "DECIMAL(10,2)"
            elif inner_type == "<class 'bool'>":
                return "BOOLEAN"
        
        return type_mapping.get(field_type, "VARCHAR(255)")
    
    def enable_all(self, app: FastAPI):
        """모든 등록된 모델에 대해 CRUD API와 관리자 페이지 활성화"""
        # 정적 파일 마운트
        if os.path.exists(self.static_dir):
            app.mount("/static", StaticFiles(directory=self.static_dir), name="static")
        
        # 각 모델에 대해 CRUD API 및 관리자 페이지 생성
        for model_name, model_class in self.registered_models.items():
            self._generate_crud_endpoints(app, model_class)
            self._generate_admin_page(app, model_class)
        
        # 메인 관리자 페이지
        self._generate_main_admin_page(app)
        
        # 앱 시작 시 테이블 생성
        @app.on_event("startup")
        async def startup_event():
            for model_class in self.registered_models.values():
                await self._create_table_if_not_exists(model_class)
    
    def _generate_crud_endpoints(self, app: FastAPI, model_class: Type):
        """데이터 클래스 기반 CRUD 엔드포인트 자동 생성"""
        model_name = model_class.__name__.lower()
        table_name = model_name
        fields_info = fields(model_class)
        
        @app.get(f"/api/{model_name}")
        async def get_items():
            """모든 아이템 조회"""
            try:
                pool = await self.mysql_manager.get_connection_pool("main")
                async with pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"SELECT * FROM {table_name}")
                        items = await cursor.fetchall()
                        return items
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get(f"/api/{model_name}/{{item_id}}")
        async def get_item(item_id: int):
            """특정 아이템 조회"""
            try:
                pool = await self.mysql_manager.get_connection_pool("main")
                async with pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (item_id,))
                        item = await cursor.fetchone()
                        if not item:
                            raise HTTPException(status_code=404, detail="Item not found")
                        return item
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post(f"/api/{model_name}")
        async def create_item(item_data: dict):
            """새 아이템 생성"""
            try:
                pool = await self.mysql_manager.get_connection_pool("main")
                async with pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        # id 필드 제외하고 나머지 필드만 사용
                        field_names = [f.name for f in fields_info if f.name != 'id']
                        values = [item_data.get(f.name) for f in fields_info if f.name != 'id']
                        
                        placeholders = ", ".join(["%s"] * len(values))
                        query = f"INSERT INTO {table_name} ({', '.join(field_names)}) VALUES ({placeholders})"
                        await cursor.execute(query, values)
                        await conn.commit()
                        
                        # 생성된 아이템 ID 반환
                        item_id = cursor.lastrowid
                        return {"id": item_id, "message": f"{model_name} created successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.put(f"/api/{model_name}/{{item_id}}")
        async def update_item(item_id: int, item_data: dict):
            """아이템 업데이트"""
            try:
                pool = await self.mysql_manager.get_connection_pool("main")
                async with pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        set_clauses = []
                        values = []
                        
                        for field in fields_info:
                            if field.name != 'id' and field.name in item_data:
                                set_clauses.append(f"{field.name} = %s")
                                values.append(item_data[field.name])
                        
                        if not set_clauses:
                            raise HTTPException(status_code=400, detail="No fields to update")
                        
                        values.append(item_id)
                        query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = %s"
                        await cursor.execute(query, values)
                        await conn.commit()
                        
                        return {"message": f"{model_name} updated successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.delete(f"/api/{model_name}/{{item_id}}")
        async def delete_item(item_id: int):
            """아이템 삭제"""
            try:
                pool = await self.mysql_manager.get_connection_pool("main")
                async with pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (item_id,))
                        await conn.commit()
                        
                        if cursor.rowcount == 0:
                            raise HTTPException(status_code=404, detail="Item not found")
                        
                        return {"message": f"{model_name} deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    def _generate_admin_page(self, app: FastAPI, model_class: Type):
        """데이터 클래스 기반 관리자 페이지 자동 생성"""
        model_name = model_class.__name__.lower()
        fields_info = fields(model_class)
        
        @app.get(f"/admin/{model_name}", response_class=HTMLResponse)
        async def admin_page(request: Request):
            """모델 관리자 페이지"""
            try:
                # 데이터 가져오기
                pool = await self.mysql_manager.get_connection_pool("main")
                async with pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"SELECT * FROM {model_name}")
                        items = await cursor.fetchall()
                
                return self.templates.TemplateResponse("model_admin.html", {
                    "request": request,
                    "model_name": model_name,
                    "model_title": model_class.__name__,
                    "fields": fields_info,
                    "items": items
                })
            except Exception as e:
                return self.templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": str(e)
                })
    
    def _generate_main_admin_page(self, app: FastAPI):
        """메인 관리자 페이지"""
        @app.get("/admin", response_class=HTMLResponse)
        async def main_admin_page(request: Request):
            """메인 관리자 페이지"""
            return self.templates.TemplateResponse("main_admin.html", {
                "request": request,
                "models": list(self.registered_models.keys())
            })
