from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.database import get_db
from app.domains.user import user_service, user_repository
from .auth_service import create_auth_tokens
from app.core.type import TokenType, LoginType, SignUpType, User

router = APIRouter()

@router.post("/signup", response_model=TokenType, status_code=status.HTTP_201_CREATED)
def signup(signup_info: SignUpType, db: Session = Depends(get_db)):
    """Create a new user"""
    # 1. 사용자 생성
    user = user_service.create_user(db, signup_info)
    
    # 2. JWT 토큰 생성 (Auth Service 사용)
    access_token = create_auth_tokens(user)

    return {"access_token": access_token}

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
    access_token = create_auth_tokens(user)

    return {"access_token": access_token}
