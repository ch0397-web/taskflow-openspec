from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import User, Message
from backend.deps import get_current_user
from backend.errors import FORBIDDEN, NOT_FOUND, TOO_LONG, VALIDATION_ERROR

router = APIRouter()


def message_to_dict(msg: Message) -> dict:
    return {
        "id": msg.id,
        "user_id": msg.user_id,
        "user_email": msg.user.email if msg.user else None,
        "content": msg.content,
        "created_at": msg.created_at,
    }


class SendMessageRequest(BaseModel):
    content: str


# GET /teams/{team_id}/messages — teams 라우터에 등록 (teams.py)
# POST /teams/{team_id}/messages — teams 라우터에 등록 (teams.py)


@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise NOT_FOUND()
    if msg.user_id != current_user.id:
        from backend.errors import NOT_OWNER
        raise NOT_OWNER()
    await db.delete(msg)
    await db.commit()
