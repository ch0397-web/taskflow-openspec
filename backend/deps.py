from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from backend.database import get_db
from backend.models import User
from backend.security import decode_token
from backend.errors import TOKEN_EXPIRED

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise TOKEN_EXPIRED()
    try:
        user_id = decode_token(credentials.credentials)
    except JWTError:
        raise TOKEN_EXPIRED()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise TOKEN_EXPIRED()
    return user
