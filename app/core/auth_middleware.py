from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.database import get_db
from app.core.config import settings
# from app.domains.user.user_repository import get_user_by_email  # 순환 import 방지

# HTTP Bearer 스키마
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """현재 인증된 사용자를 반환하는 의존성"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Bearer 토큰에서 실제 토큰 추출
        token = credentials.credentials
        
        # 토큰 검증
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        email = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 사용자 조회 (순환 import 방지를 위해 함수 내에서 import)
    from app.domains.user.user_repository import get_user_by_email
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user = Depends(get_current_user)):
    """현재 활성화된 사용자를 반환하는 의존성"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user
