from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Instance spec constants (not a DB model — reference data)
# ---------------------------------------------------------------------------

class SpecItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    spec_id: str
    name: str
    vcpu: int
    ram_gb: int
    system_disk_gb: int
    monthly_price: int


class SpecCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    economy: list[SpecItem]
    high_performance: list[SpecItem]


INSTANCE_SPECS: dict[str, dict] = {
    "eco-2c2g": {
        "spec_id": "eco-2c2g",
        "instance_type": "economy",
        "name": "通用计算机",
        "vcpu": 2,
        "ram_gb": 2,
        "system_disk_gb": 40,
        "monthly_price": 100,
    },
    "eco-2c4g": {
        "spec_id": "eco-2c4g",
        "instance_type": "economy",
        "name": "通用计算机",
        "vcpu": 2,
        "ram_gb": 4,
        "system_disk_gb": 40,
        "monthly_price": 140,
    },
    "eco-2c8g": {
        "spec_id": "eco-2c8g",
        "instance_type": "economy",
        "name": "通用计算机",
        "vcpu": 2,
        "ram_gb": 8,
        "system_disk_gb": 40,
        "monthly_price": 180,
    },
    "eco-4c8g": {
        "spec_id": "eco-4c8g",
        "instance_type": "economy",
        "name": "通用计算机",
        "vcpu": 4,
        "ram_gb": 8,
        "system_disk_gb": 40,
        "monthly_price": 240,
    },
    "perf-2c4g": {
        "spec_id": "perf-2c4g",
        "instance_type": "high_performance",
        "name": "通用增强计算机",
        "vcpu": 2,
        "ram_gb": 4,
        "system_disk_gb": 40,
        "monthly_price": 160,
    },
    "perf-2c8g": {
        "spec_id": "perf-2c8g",
        "instance_type": "high_performance",
        "name": "通用增强计算机",
        "vcpu": 2,
        "ram_gb": 8,
        "system_disk_gb": 40,
        "monthly_price": 200,
    },
    "perf-4c8g": {
        "spec_id": "perf-4c8g",
        "instance_type": "high_performance",
        "name": "通用增强计算机",
        "vcpu": 4,
        "ram_gb": 8,
        "system_disk_gb": 40,
        "monthly_price": 260,
    },
    "perf-8c16g": {
        "spec_id": "perf-8c16g",
        "instance_type": "high_performance",
        "name": "通用增强计算机",
        "vcpu": 8,
        "ram_gb": 16,
        "system_disk_gb": 40,
        "monthly_price": 500,
    },
}


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CreateHostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    hostname: str
    billing_mode: str
    instance_type: str
    spec_id: str
    os_image: str
    ip_mode: str
    ip_address: Optional[str] = None
    ip_mask: Optional[int] = None
    username: str
    password: str
    duration: int


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class HostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    hostname: str
    billing_mode: str
    instance_type: str
    vcpu: int
    ram_gb: int
    os_image: str
    ip_mode: str
    ip_address: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class HostDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    hostname: str
    billing_mode: str
    instance_type: str
    spec_id: str
    vcpu: int
    ram_gb: int
    system_disk_gb: int
    os_image: str
    ip_mode: str
    ip_address: Optional[str] = None
    ip_mask: Optional[int] = None
    status: str
    error_msg: Optional[str] = None
    duration: int
    unit_price: float
    cost_info: Optional[dict] = None
    username: str
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PaginatedHostList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[HostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str
    error_code: str
    message: str
