from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth_middleware import get_current_active_user
from app.domains.user.user_models import User

router = APIRouter()

@router.get("/me", response_model=dict)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user information (JWT 인증 필요)"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active
    }

@router.get("/public")
def read_public_info():
    return {"message": "This is public information"}

@router.get("/protected")
def read_protected_info(current_user: User = Depends(get_current_active_user)):
    return {
        "message": f"Hello {current_user.email}! This is protected information.",
        "user_id": current_user.id
    }