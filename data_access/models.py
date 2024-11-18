from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    DateTime,
    Boolean,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    is_connected = Column(Boolean, default=False, nullable=False)
    creation_date = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    update_date = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    files = relationship("File", back_populates="user")

    __table_args__ = (
        CheckConstraint("update_date >= creation_date", name="check_update_date"),
    )


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    size = Column(Integer, nullable=False)
    creation_date = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    update_date = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="files")
    tags = relationship("Tag", secondary=file_tags, back_populates="files")

    __table_args__ = (
        UniqueConstraint("name", "file_type", "user_id", name="uq_name_type_by_user"),
        CheckConstraint("update_date >= creation_date", name="check_update_date"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    files = relationship("File", secondary=file_tags, back_populates="tags")
