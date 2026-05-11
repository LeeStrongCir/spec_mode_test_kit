import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.user import Base


class LoginStatus(str, enum.Enum):
    success = "success"
    failed = "failed"


class UserType(str, enum.Enum):
    user = "user"
    admin = "admin"


class LoginRecord(Base):
    __tablename__ = "login_records"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    login_time = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ip_address = Column(String(45), nullable=False)
    device_type = Column(String(50), nullable=False, default="unknown")
    browser = Column(String(100), nullable=False, default="unknown")
    operating_system = Column(String(100), nullable=False, default="unknown")
    status = Column(SAEnum(LoginStatus), nullable=False)
    failure_reason = Column(String(255), nullable=True)
    is_anomalous = Column(Boolean, nullable=False, default=False)
    ip_geo_location = Column(String(255), nullable=True)
    user_type = Column(SAEnum(UserType), nullable=False, default=UserType.user)
