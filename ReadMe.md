# yh-base: Database Management Package

yh-db, yh-redis, yh-config 패키지를 포함한 데이터베이스 관리 라이브러리입니다.

## 🚀 설치 방법

### 1. Git URL로 직접 설치 (권장)

#### MySQL만 사용하는 앱
```bash
pip install "git+https://github.com/yourusername/yh-base.git#egg=yh-base[mysql]"
```

#### Redis만 사용하는 앱
```bash
pip install "git+https://github.com/yourusername/yh-base.git#egg=yh-base[redis]"
```

#### MySQL + Redis 모두 사용하는 앱
```bash
pip install "git+https://github.com/yourusername/yh-base.git#egg=yh-base[mysql,redis]"
```

#### 개발 도구 포함
```bash
pip install "git+https://github.com/yourusername/yh-base.git#egg=yh-base[mysql,redis,dev]"
```

### 2. requirements.txt에 추가
```txt
# requirements.txt
git+https://github.com/yourusername/yh-base.git#egg=yh-base[mysql,redis]
fastapi>=0.100.0
uvicorn>=0.20.0
```

### 3. 특정 버전/브랜치 사용
```bash
# 특정 브랜치
pip install "git+https://github.com/yourusername/yh-base.git@develop#egg=yh-base[mysql,redis]"

# 특정 커밋
pip install "git+https://github.com/yourusername/yh-base.git@abc1234#egg=yh-base[mysql,redis]"
```

## 💻 사용 예시

### 기본 사용법
```python
import asyncio
from yh_config import ConfigManager
from yh_db import MySQLManager, MySQLConfig
from yh_redis import RedisManager, RedisConfig

async def main():
    # 설정 로드
    config_manager = ConfigManager("config/database.yaml")
    db_config = config_manager.get_config("database")
    
    # MySQL 설정
    mysql_configs = [
        MySQLConfig(
            dbNameKey="main",
            host=db_config["mysql"]["main"]["host"],
            port=db_config["mysql"]["main"]["port"],
            user=db_config["mysql"]["main"]["user"],
            password=db_config["mysql"]["main"]["password"],
            database=db_config["mysql"]["main"]["database"]
        )
    ]
    
    # Redis 설정
    redis_config = RedisConfig(
        host=db_config["redis"]["main"]["host"],
        port=db_config["redis"]["main"]["port"],
        db=db_config["redis"]["main"]["db"],
        decode_responses=db_config["redis"]["main"]["decode_responses"]
    )
    
    # Manager 초기화
    mysql_manager = MySQLManager(mysql_configs)
    redis_manager = RedisManager(redis_config)
    
    await mysql_manager.initialize()
    await redis_manager.initialize()
    
    # 사용
    connection = await mysql_manager.get_connection("main")
    redis_client = await redis_manager.get_redis_client()
    
    print("Database connections ready!")

if __name__ == "__main__":
    asyncio.run(main())
```

### 설정 파일 예시
```yaml
# config/database.yaml
database:
  mysql:
    main:
      host: localhost
      port: 3306
      user: testuser
      password: testpassword
      database: testdb
  redis:
    main:
      host: localhost
      port: 6379
      db: 0
      decode_responses: true
```

## 🧪 테스트 실행

### 모든 테스트 실행
```bash
pytest
```

### 특정 패키지 테스트만
```bash
# MySQL 테스트만
pytest tests/yh_db/

# Redis 테스트만
pytest tests/yh_redis/

# Config 테스트만
pytest tests/yh_config/
```

### 병렬 테스트 실행
```bash
pytest -n auto
```

## 🐳 Docker 개발환경

### docker-compose.yml
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: testdb
      MYSQL_USER: testuser
      MYSQL_PASSWORD: testpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    environment:
      - MYSQL_HOST=mysql
      - REDIS_HOST=redis
    volumes:
      - .:/app

volumes:
  mysql_data:
  redis_data:
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install base package
RUN pip install "git+https://github.com/yourusername/yh-base.git#egg=yh-base[mysql,redis]"

# Install app dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔄 CI/CD 구성

### GitHub Actions 예시
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: rootpassword
          MYSQL_DATABASE: testdb
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=3
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install base package
      run: |
        python -m pip install --upgrade pip
        pip install "git+https://github.com/yourusername/yh-base.git#egg=yh-base[mysql,redis,dev]"
    
    - name: Install app dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest -v --cov=yh_db --cov=yh_redis --cov=yh_config
```

## 📦 패키지 크기 비교

- **기본**: 0MB (코어만)
- **MySQL**: +15MB
- **Redis**: +10MB  
- **DynamoDB**: +50MB
- **Memcached**: +5MB
- **Prometheus**: +8MB
- **Dev tools**: +20MB

**전체**: ~108MB vs **필요한 것만**: 5-30MB

## 🏷️ 버전 관리

### Git 태그로 버전 관리
```bash
# 버전 태그 생성
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 특정 버전 사용
pip install "git+https://github.com/yourusername/yh-base.git@v1.0.0#egg=yh-base[mysql,redis]"
```

### 버전별 설치
```bash
# 최신 버전
pip install "git+https://github.com/yourusername/yh-base.git#egg=yh-base[mysql,redis]"

# 특정 버전
pip install "git+https://github.com/yourusername/yh-base.git@v1.0.0#egg=yh-base[mysql,redis]"

# 개발 버전
pip install "git+https://github.com/yourusername/yh-base.git@develop#egg=yh-base[mysql,redis]"
```
