from sqlalchemy.orm import Session
from . import user_models
from app.core.type import SignUpType

# 이메일로 사용자 조회
def get_user_by_email(db: Session, email: str):
    return db.query(user_models.User).filter(user_models.User.email == email).first()

# 사용자 생성
def create_user(db: Session, user: SignUpType, hashed_password: str):
    db_user = user_models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 특정 ID로 사용자 조회
def get_user(db: Session, user_id: int):
    return db.query(user_models.User).filter(user_models.User.id == user_id).first()

# 여러 사용자 조회 (페이지네이션)
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(user_models.User).offset(skip).limit(limit).all()

