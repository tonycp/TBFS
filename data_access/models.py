from __future__ import annotations

from typing import List
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Table,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import datetime


class Base(DeclarativeBase):
    pass


file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", ForeignKey("files.id")),
    Column("tag_id", ForeignKey("tags.id")),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    is_connected: Mapped[bool] = mapped_column(default=False, nullable=False)
    creation_date: Mapped[DateTime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    update_date: Mapped[DateTime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    files: Mapped[List[File]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("update_date >= creation_date", name="check_update_date"),
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, is_connected={self.is_connected!r})"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)

    creation_date: Mapped[DateTime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    update_date: Mapped[DateTime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship(
        back_populates="files", cascade="all, delete-orphan"
    )

    tags: Mapped[List[Tag]] = relationship(
        secondary=file_tags, back_populates="file", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("name", "file_type", "user_id", name="uq_name_type_by_user"),
        CheckConstraint("update_date >= creation_date", name="check_update_date"),
    )

    def __repr__(self) -> str:
        return f"File(id={self.id!r}, name={self.name!r}, file_type={self.file_type!r}, size={self.size!r})"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    creation_date: Mapped[DateTime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    update_date: Mapped[DateTime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    file: Mapped[List[File]] = relationship(
        secondary=file_tags, back_populates="tag", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r})"
