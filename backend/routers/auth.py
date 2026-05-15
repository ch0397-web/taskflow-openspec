import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models import User
from backend.security import hash_password, verify_password, create_access_token
from backend.deps import get_current_user
from backend.errors import EMAIL_TAKEN, INVALID_CREDENTIALS, VALIDATION_ERROR

router = APIRouter()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def user_response(user: User, token: str) -> dict:
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "team_id": user.team_id},
    }


@router.post("/signup", status_code=201)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    if not EMAIL_RE.match(body.email):
        raise VALIDATION_ERROR("올바른 이메일 형식이 아닙니다")
    if len(body.password) < 8:
        raise VALIDATION_ERROR("비밀번호는 8자 이상이어야 합니다")

    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise EMAIL_TAKEN()

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user_response(user, create_access_token(user.id))


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise INVALID_CREDENTIALS()
    return user_response(user, create_access_token(user.id))


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "team_id": current_user.team_id}


@router.post("/logout")
async def logout():
    return {}
