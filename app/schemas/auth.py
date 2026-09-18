from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole
from app.schemas.user import UserRead

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.CITIZEN
    phone: Optional[str] = None
    village: Optional[str] = None
    ward: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
