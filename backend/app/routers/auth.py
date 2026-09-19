"""FastAPI Router for User Authentication & JWT Token Exchange."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database import get_db
from backend.app.models.entities import User, HospitalUser, Hospital
from backend.app.utils.security import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 7200
    user_role: str = "disaster_officer"
    hospital_id: Optional[int] = None
    hospital_name: Optional[str] = None


class RegisterUserRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "disaster_officer"


@router.post("/token", response_model=TokenResponse, summary="OAuth2 JWT Token Login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Exchange username/email and password for a JWT access token.
    For hospital users, hospital_id is embedded in the JWT payload."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        # Demo fallback check if DB user is not yet created
        if form_data.username == "admin@sih26191.gov.in" and form_data.password == "AdminDisaster#2026":
            token = create_access_token({"sub": "admin@sih26191.gov.in", "role": "disaster_officer"})
            return TokenResponse(access_token=token)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # For hospital role: embed hospital_id in JWT
    token_data: dict = {"sub": user.email, "role": user.role}
    hospital_id = None
    hospital_name = None

    if user.role == "hospital":
        hospital_user = db.query(HospitalUser).filter(HospitalUser.user_id == user.id).first()
        if not hospital_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No hospital association found for this account. Contact administrator.",
            )
        if hospital_user.verification_status != "VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Hospital account is {hospital_user.verification_status}. Contact administrator.",
            )
        hospital = db.query(Hospital).filter(Hospital.id == hospital_user.hospital_id).first()
        if hospital:
            token_data["hospital_id"] = hospital.id
            hospital_id = hospital.id
            hospital_name = hospital.name

    token = create_access_token(token_data)
    return TokenResponse(
        access_token=token,
        user_role=user.role,
        hospital_id=hospital_id,
        hospital_name=hospital_name,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Register User Account")
def register_user(req: RegisterUserRequest, db: Session = Depends(get_db)):
    """Register user account with bcrypt hashed password."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    new_user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()

    token = create_access_token({"sub": new_user.email, "role": new_user.role})
    return TokenResponse(access_token=token, user_role=new_user.role)
