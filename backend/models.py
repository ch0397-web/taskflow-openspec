from datetime import datetime, timezone
from sqlalchemy import (
    Integer, String, Text, DateTime, ForeignKey, Index, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    team_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team: Mapped["Team | None"] = relationship("Team", foreign_keys=[team_id], back_populates="members")
    created_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="user")

    __table_args__ = (Index("ix_users_team_id", "team_id"),)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(9), unique=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])
    members: Mapped[list["User"]] = relationship("User", foreign_keys="User.team_id", back_populates="team")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="team", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="team", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_teams_invite_code", "invite_code"),)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(SAEnum("TODO", "DOING", "DONE", name="task_status"), nullable=False, default="TODO")
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team: Mapped["Team"] = relationship("Team", back_populates="tasks")
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee: Mapped["User | None"] = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")

    __table_args__ = (Index("ix_tasks_team_created", "team_id", "created_at"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team: Mapped["Team"] = relationship("Team", back_populates="messages")
    user: Mapped["User"] = relationship("User", back_populates="messages")

    __table_args__ = (Index("ix_messages_team_created", "team_id", "created_at"),)
