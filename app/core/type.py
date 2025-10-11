from pydantic import BaseModel, EmailStr


class TokenType(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class LoginType(BaseModel):
    email: EmailStr
    password: str

class SignUpType(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True