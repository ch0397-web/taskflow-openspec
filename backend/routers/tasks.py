from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import User, Team, Task
from backend.deps import get_current_user
from backend.errors import FORBIDDEN, NOT_FOUND, VALIDATION_ERROR

router = APIRouter()

VALID_STATUSES = {"TODO", "DOING", "DONE"}


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


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    assignee_id: Optional[int] = None


class UpdateStatusRequest(BaseModel):
    status: str


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise NOT_FOUND()
    if current_user.team_id != task.team_id:
        raise FORBIDDEN()
    return task_to_dict(task)


@router.patch("/{task_id}/status")
async def update_task_status(
    task_id: int,
    body: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.status not in VALID_STATUSES:
        raise VALIDATION_ERROR("상태는 TODO, DOING, DONE 중 하나여야 합니다")

    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise NOT_FOUND()
    if current_user.team_id != task.team_id:
        raise FORBIDDEN()

    task.status = body.status
    await db.commit()

    result2 = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
    )
    return task_to_dict(result2.scalar_one())


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    body: UpdateTaskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise NOT_FOUND()
    if current_user.team_id != task.team_id:
        raise FORBIDDEN()

    if body.title is not None:
        if not 1 <= len(body.title) <= 100:
            raise VALIDATION_ERROR("제목은 1~100자여야 합니다")
        task.title = body.title
    if "assignee_id" in body.model_fields_set:
        task.assignee_id = body.assignee_id

    await db.commit()

    result2 = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
    )
    return task_to_dict(result2.scalar_one())


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NOT_FOUND()
    if current_user.team_id != task.team_id:
        raise FORBIDDEN()

    team_result = await db.execute(select(Team).where(Team.id == task.team_id))
    team = team_result.scalar_one()

    if task.creator_id != current_user.id and team.owner_id != current_user.id:
        raise FORBIDDEN()

    await db.delete(task)
    await db.commit()
