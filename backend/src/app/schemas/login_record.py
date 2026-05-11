from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoginRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    login_time: datetime
    ip_address: str
    ip_geo_location: Optional[str] = None
    device_type: str
    browser: str
    operating_system: str
    status: str
    failure_reason: Optional[str] = None
    is_anomalous: bool


class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class LoginRecordListResponse(BaseModel):
    status: str = "success"
    records: list[LoginRecordResponse]
    pagination: PaginationInfo
