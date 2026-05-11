import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.user import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    access_token_jti = Column(String(36), unique=True, nullable=False)
    refresh_token_hash = Column(String(255), unique=True, nullable=False)
    access_token_expires_at = Column(DateTime(timezone=True), nullable=False)
    refresh_token_expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)


class AccountLock(Base):
    __tablename__ = "account_locks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    locked_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    unlock_at = Column(DateTime(timezone=True), nullable=False)
    failed_attempts = Column(SmallInteger, nullable=False)
    lock_reason = Column(String(255), nullable=False)
    released_at = Column(DateTime(timezone=True), nullable=True)
    released_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
