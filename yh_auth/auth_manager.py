from typing import NamedTuple, Optional
from .auth_role import AuthRole
import jwt
import datetime

class AuthConfig(NamedTuple):
    accessSecretKey: str  # Access Token용 시크릿 키
    refreshSecretKey: str  # Refresh Token용 시크릿 키
    accessExpHours: int = 24  # Access Token 만료시간 (시간)
    refreshExpDays: int = 30  # Refresh Token 만료시간 (일)

class AuthParameters(NamedTuple):
    name: Optional[str]
    email: Optional[str]
    userId: int
    role: Optional[str] = AuthRole.USER

class AuthManager:
    def __init__(self, config: AuthConfig):
        self.config = config

    def getAccessToken(self, parameters: AuthParameters):
        """Access Token과 Refresh Token 생성"""
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Access Token 페이로드 (짧은 만료시간)
        access_exp = now + datetime.timedelta(hours=self.config.accessExpHours)
        access_payload = {
            "name": parameters.name,
            "email": parameters.email,
            "userId": parameters.userId,
            "role": parameters.role.value if hasattr(parameters.role, 'value') else parameters.role,
            "exp": access_exp,
            "iat": now,
            "type": "access"
        }
        
        # 토큰 생성
        access_token = jwt.encode(
            access_payload,
            self.config.accessSecretKey,
            algorithm="HS256"
        )
        
        return access_token
    
    def getRefreshToken(self, parameters: AuthParameters):
        """Refresh Token 생성"""
        now = datetime.datetime.now(datetime.timezone.utc)
        refresh_exp = now + datetime.timedelta(days=self.config.refreshExpDays)
        refresh_payload = {
            "name": parameters.name,
            "email": parameters.email,
            "userId": parameters.userId,
            "role": parameters.role.value if hasattr(parameters.role, 'value') else parameters.role,
            "exp": refresh_exp,
            "iat": now,
            "type": "refresh"
        }
        return jwt.encode(
            refresh_payload,
            self.config.refreshSecretKey,
            algorithm="HS256"
        )
    
    def verifyAccessToken(self, access_token: str) -> AuthParameters:
        """Access Token 검증"""
        try:
            payload = jwt.decode(
                access_token, 
                self.config.accessSecretKey, 
                algorithms=["HS256"]
            )
            
            # 토큰 타입 확인
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
                
            return AuthParameters(
                name=payload.get("name"),
                email=payload.get("email"),
                userId=payload["userId"],
                role=payload.get("role")
            )
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Access token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid access token")
    
    def verifyRefreshToken(self, refresh_token: str) -> AuthParameters:
        """Refresh Token 검증"""
        try:
            payload = jwt.decode(
                refresh_token, 
                self.config.refreshSecretKey, 
                algorithms=["HS256"]
            )
            
            # 토큰 타입 확인
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
                
            return AuthParameters(
                name=payload.get("name"),
                email=payload.get("email"),
                userId=payload["userId"],
                role=payload.get("role")
            )
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token")
    
    def refreshByRefreshToken(self, refresh_token: str) -> AuthParameters:
        """Refresh Token을 사용하여 새로운 Access Token 생성"""
        try:
            payload = self.verifyRefreshToken(refresh_token)
            return self.getAccessToken(payload)
        except Exception as e:
            raise ValueError(f"Failed to refresh access token: {e}")
