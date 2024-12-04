from __future__ import annotations

from typing import List
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Table,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", ForeignKey("files.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    is_connected: Mapped[bool] = mapped_column(default=False, nullable=False)
    creation_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )

    files: Mapped[List[File]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("update_date >= creation_date", name="check_update_date"),
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, is_connected={self.is_connected!r})"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)

    creation_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship(
        back_populates="files",
        single_parent=True,
    )

    tags: Mapped[List[Tag]] = relationship(
        secondary=file_tags,
        back_populates="files",
        cascade="all",
    )

    sources: Mapped[List[FileSource]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    __table_args__ = (
        UniqueConstraint("name", "file_type", "user_id", name="uq_name_type_by_user"),
    )

    def __repr__(self) -> str:
        return f"File(id={self.id!r}, name={self.name!r}, file_type={self.file_type!r}, size={self.size!r})"


class FileSource(Base):
    __tablename__ = "file_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))
    chunk_size: Mapped[int] = mapped_column(nullable=False)
    chunk_number: Mapped[int] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)

    creation_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )

    file: Mapped[File] = relationship(
        back_populates="sources",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    def __repr__(self) -> str:
        return f"FileSource(id={self.id!r}, file_id={self.file_id!r}, chunk_size={self.chunk_size!r}, chunk_number={self.chunk_number!r}, url={self.url!r})"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    creation_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )

    files: Mapped[List[File]] = relationship(
        secondary=file_tags,
        back_populates="tags",
    )

    __table_args__ = (
        CheckConstraint("update_date >= creation_date", name="check_update_date"),
    )

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r})"
