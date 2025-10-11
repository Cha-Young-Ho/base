from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.database import get_db
from app.domains.user import user_service, user_repository
from .auth_service import create_auth_tokens, verify_refresh_token
from app.core.type import TokenType, LoginType, SignUpType, User

router = APIRouter()

@router.post("/signup", response_model=TokenType, status_code=status.HTTP_201_CREATED)
def signup(signup_info: SignUpType, db: Session = Depends(get_db)):
    """Create a new user"""
    # 1. 사용자 생성
    user = user_service.create_user(db, signup_info)
    
    # 2. JWT 토큰 생성 (Auth Service 사용)
    access_token, refresh_token = create_auth_tokens(user)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/login", response_model=TokenType)
def login_for_access_token(auth_login: LoginType, db: Session = Depends(get_db)):
    # 1. 사용자 인증 (User Service 사용)
    user = user_service.authenticate_user(db, auth_login.email, auth_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. JWT 토큰 생성 (Auth Service 사용)
    access_token, refresh_token = create_auth_tokens(user)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenType)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh Token으로 새로운 Access Token 발급"""
    try:
        # 1. Refresh Token 검증 (Auth Service 사용)
        payload = verify_refresh_token(refresh_token)
        email = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # 2. 사용자 확인 (User Service 사용)
        user = user_repository.get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # 3. 새로운 토큰 생성 (Auth Service 사용)
        access_token, new_refresh_token = create_auth_tokens(user)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
