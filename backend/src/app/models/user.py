import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserStatus(str, enum.Enum):
    active = "active"
    locked = "locked"
    disabled = "disabled"


class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)
    failed_login_count = Column(SmallInteger, nullable=False, default=0)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
