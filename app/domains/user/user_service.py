from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import hashlib
import secrets
from . import user_repository
from app.core.type import SignUpType, User

def get_password_hash(password: str):
    """비밀번호 해시화 (간단한 방법)"""
    # 실제 프로덕션에서는 bcrypt나 argon2 사용 권장
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{hashed.hex()}"

def verify_password(plain_password: str, hashed_password: str):
    """비밀번호 검증"""
    try:
        salt, stored_hash = hashed_password.split(':')
        hashed = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hashed.hex() == stored_hash
    except:
        return False

def create_user(db: Session, user: SignUpType):
    """사용자 생성"""
    db_user = user_repository.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    return user_repository.create_user(db=db, user=user, hashed_password=hashed_password)

def get_user_by_email(db: Session, email: str):
    """이메일로 사용자 조회"""
    return user_repository.get_user_by_email(db, email=email)

def get_user_by_id(db: Session, user_id: int):
    """ID로 사용자 조회"""
    return user_repository.get_user(db, user_id=user_id)

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """모든 사용자 조회 (페이지네이션)"""
    return user_repository.get_users(db, skip=skip, limit=limit)

def authenticate_user(db: Session, email: str, password: str):
    """사용자 인증 (이메일/비밀번호 확인)"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user