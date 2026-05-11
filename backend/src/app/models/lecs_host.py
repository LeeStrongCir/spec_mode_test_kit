import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.user import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HostStatus(str, enum.Enum):
    creating = "creating"
    normal = "normal"
    failed = "failed"
    shutting_down = "shutting_down"
    stopped = "stopped"
    starting = "starting"
    deleting = "deleting"
    deleted = "deleted"


class LECSHost(Base):
    __tablename__ = "lecs_hosts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    hostname = Column(String(64), nullable=False)
    billing_mode = Column(String(16), nullable=False)
    instance_type = Column(String(32), nullable=False)
    spec_id = Column(String(32), nullable=False)
    vcpu = Column(Integer, nullable=False)
    ram_gb = Column(Integer, nullable=False)
    system_disk_gb = Column(Integer, nullable=False)
    os_image = Column(String(32), nullable=False)
    ip_mode = Column(String(16), nullable=False)
    ip_address = Column(String(45), nullable=True)
    ip_mask = Column(Integer, nullable=True)
    status = Column(SAEnum(HostStatus), nullable=False, default=HostStatus.creating)
    error_msg = Column(Text, nullable=True)
    duration = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    cost_info = Column(JSON, nullable=True)
    username = Column(String(64), nullable=False)
    password_hash = Column(String(255), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )

    __table_args__ = (
        Index("ix_lecs_hosts_user_id_deleted_at", "user_id", "deleted_at"),
    )
