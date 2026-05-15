import re
import random
import string
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import User, Team, Task, Message
from backend.deps import get_current_user
from backend.errors import (
    VALIDATION_ERROR, ALREADY_IN_TEAM, NOT_FOUND, FORBIDDEN, OWNER_CANNOT_LEAVE
)

router = APIRouter()

INVITE_CODE_RE = re.compile(r"^[A-Z]{4}-[0-9]{4}$")


def generate_invite_code() -> str:
    letters = "".join(random.choices(string.ascii_uppercase, k=4))
    digits = "".join(random.choices(string.digits, k=4))
    return f"{letters}-{digits}"


async def get_team_or_403(team_id: int, user: User) -> None:
    if user.team_id != team_id:
        raise FORBIDDEN()


class CreateTeamRequest(BaseModel):
    name: str


class JoinTeamRequest(BaseModel):
    invite_code: str


class CreateTaskRequest(BaseModel):
    title: str
    assignee_id: Optional[int] = None


def task_to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "team_id": task.team_id,
        "creator_id": task.creator_id,
        "creator_email": task.creator.email if task.creator else None,
        "assignee_id": task.assignee_id,
        "assignee_email": task.assignee.email if task.assignee else None,
        "created_at": task.created_at,
    }


@router.post("", status_code=201)
async def create_team(
    body: CreateTeamRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not 1 <= len(body.name) <= 30:
        raise VALIDATION_ERROR("팀 이름은 1~30자여야 합니다")

    invite_code = generate_invite_code()
    team = Team(name=body.name, invite_code=invite_code, owner_id=current_user.id)
    db.add(team)
    await db.flush()

    current_user.team_id = team.id
    await db.commit()
    await db.refresh(team)
    return {
        "id": team.id,
        "name": team.name,
        "invite_code": team.invite_code,
        "owner_id": team.owner_id,
        "created_at": team.created_at,
    }


@router.post("/join")
async def join_team(
    body: JoinTeamRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not INVITE_CODE_RE.match(body.invite_code):
        raise VALIDATION_ERROR("초대코드 형식이 올바르지 않습니다 (예: ABCD-1234)")
    if current_user.team_id is not None:
        raise ALREADY_IN_TEAM()

    result = await db.execute(select(Team).where(Team.invite_code == body.invite_code))
    team = result.scalar_one_or_none()
    if not team:
        raise NOT_FOUND()

    member_count_result = await db.execute(
        select(func.count()).where(User.team_id == team.id)
    )
    member_count = member_count_result.scalar()

    current_user.team_id = team.id
    await db.commit()
    return {
        "team": {"id": team.id, "name": team.name, "member_count": member_count + 1},
        "redirect": f"/teams/{team.id}",
    }


@router.get("/{team_id}")
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_team_or_403(team_id, current_user)
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise NOT_FOUND()
    return {
        "id": team.id,
        "name": team.name,
        "invite_code": team.invite_code,
        "owner_id": team.owner_id,
        "created_at": team.created_at,
    }


@router.get("/{team_id}/members")
async def get_members(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_team_or_403(team_id, current_user)
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise NOT_FOUND()

    members_result = await db.execute(select(User).where(User.team_id == team_id))
    members = members_result.scalars().all()
    return [
        {
            "id": m.id,
            "email": m.email,
            "is_owner": m.id == team.owner_id,
            "joined_at": m.created_at,
        }
        for m in members
    ]


@router.delete("/{team_id}/leave")
async def leave_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_team_or_403(team_id, current_user)
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise NOT_FOUND()
    if team.owner_id == current_user.id:
        raise OWNER_CANNOT_LEAVE()

    current_user.team_id = None
    await db.commit()
    return {}


@router.get("/{team_id}/tasks")
async def list_tasks(
    team_id: int,
    assignee: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_team_or_403(team_id, current_user)
    query = (
        select(Task)
        .where(Task.team_id == team_id)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
        .order_by(Task.created_at.desc())
    )
    if assignee == "me":
        query = query.where(Task.assignee_id == current_user.id)
    elif assignee == "unassigned":
        query = query.where(Task.assignee_id.is_(None))
    result = await db.execute(query)
    return [task_to_dict(t) for t in result.scalars().all()]


@router.post("/{team_id}/tasks", status_code=201)
async def create_task(
    team_id: int,
    body: CreateTaskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_team_or_403(team_id, current_user)
    from backend.errors import VALIDATION_ERROR
    if not 1 <= len(body.title) <= 100:
        raise VALIDATION_ERROR("제목은 1~100자여야 합니다")

    task = Task(
        team_id=team_id,
        title=body.title,
        status="TODO",
        creator_id=current_user.id,
        assignee_id=body.assignee_id,
    )
    db.add(task)
    await db.commit()

    result = await db.execute(
        select(Task)
        .where(Task.id == task.id)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
    )
    return task_to_dict(result.scalar_one())


# ── 채팅 라우트 ──────────────────────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    content: str


def message_to_dict(msg: Message) -> dict:
    return {
        "id": msg.id,
        "user_id": msg.user_id,
        "user_email": msg.user.email if msg.user else None,
        "content": msg.content,
        "created_at": msg.created_at,
    }


@router.get("/{team_id}/messages")
async def list_messages(
    team_id: int,
    since: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_team_or_403(team_id, current_user)
    from backend.errors import VALIDATION_ERROR

    query = (
        select(Message)
        .where(Message.team_id == team_id)
        .options(selectinload(Message.user))
        .order_by(Message.created_at.asc())
    )
    if since:
        try:
            from datetime import datetime, timezone
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            query = query.where(Message.created_at > since_dt)
        except ValueError:
            raise VALIDATION_ERROR("since 파라미터 형식이 올바르지 않습니다")
    else:
        from sqlalchemy import desc
        subq = (
            select(Message.id)
            .where(Message.team_id == team_id)
            .order_by(desc(Message.created_at))
            .limit(50)
            .scalar_subquery()
        )
        query = query.where(Message.id.in_(subq))

    result = await db.execute(query)
    return [message_to_dict(m) for m in result.scalars().all()]


@router.post("/{team_id}/messages", status_code=201)
async def send_message(
    team_id: int,
    body: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_team_or_403(team_id, current_user)
    from backend.errors import TOO_LONG, VALIDATION_ERROR

    if not body.content or len(body.content.strip()) == 0:
        raise VALIDATION_ERROR("메시지를 입력해주세요")
    if len(body.content) > 1000:
        raise TOO_LONG(len(body.content))

    msg = Message(team_id=team_id, user_id=current_user.id, content=body.content)
    db.add(msg)
    await db.commit()

    result = await db.execute(
        select(Message)
        .where(Message.id == msg.id)
        .options(selectinload(Message.user))
    )
    return message_to_dict(result.scalar_one())
