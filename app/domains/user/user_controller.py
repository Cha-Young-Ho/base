from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/me")
def read_current_user():
    """Get current user information"""
    return {"email": "fakeuser@example.com", "is_active": True}