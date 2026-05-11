import math
import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lecs_host import HostStatus, LECSHost
from app.models.user import User
from app.schemas.lecs_host import CreateHostRequest
from app.services.password_service import hash_password


async def list_hosts(
    db: AsyncSession,
    user: User,
    page: int = 1,
    page_size: int = 20,
    is_admin: bool = False,
) -> tuple[list, int, int, int, int]:
    """Return (items, total, page, page_size, total_pages).

    Filters: deleted_at IS NULL AND (user_id=current_user.id OR admin sees all).
    Order: created_at DESC with pagination.
    """
    base_filter = LECSHost.deleted_at.is_(None)

    if not is_admin:
        base_filter = LECSHost.deleted_at.is_(None) & (LECSHost.user_id == user.id)

    count_stmt = select(func.count()).select_from(LECSHost).where(base_filter)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    list_stmt = (
        select(LECSHost)
        .where(base_filter)
        .order_by(LECSHost.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(list_stmt)
    items = result.scalars().all()

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return items, total, page, page_size, total_pages


async def get_host_by_id(
    db: AsyncSession,
    host_id: uuid.UUID,
    user: User,
    is_admin: bool = False,
) -> Optional[LECSHost]:
    """Return LECSHost or None. Scope: user_id matches (admin sees all), deleted_at IS NULL."""
    stmt = select(LECSHost).where(LECSHost.deleted_at.is_(None), LECSHost.id == host_id)

    if not is_admin:
        stmt = stmt.where(LECSHost.user_id == user.id)

    result = await db.execute(stmt)
    return result.scalars().first()


async def create_host(
    db: AsyncSession,
    user: User,
    request: CreateHostRequest,
    cost_info_dict: dict,
) -> LECSHost:
    """Create LECSHost with status='creating', hash password, return the new host."""
    from app.schemas.lecs_host import INSTANCE_SPECS

    spec = INSTANCE_SPECS[request.spec_id]

    host = LECSHost(
        user_id=user.id,
        hostname=request.hostname,
        billing_mode=request.billing_mode,
        instance_type=request.instance_type,
        spec_id=request.spec_id,
        vcpu=spec["vcpu"],
        ram_gb=spec["ram_gb"],
        system_disk_gb=spec["system_disk_gb"],
        os_image=request.os_image,
        ip_mode=request.ip_mode,
        ip_address=request.ip_address,
        ip_mask=request.ip_mask,
        status=HostStatus.creating,
        duration=request.duration,
        unit_price=spec["monthly_price"],
        cost_info=cost_info_dict,
        username=request.username,
        password_hash=hash_password(request.password),
    )

    db.add(host)
    await db.commit()
    await db.refresh(host)

    return host


async def check_quota(
    db: AsyncSession,
    user_id: uuid.UUID,
    max_hosts: int = 100,
) -> bool:
    """Return True if user can create another host (count < max_hosts)."""
    count_stmt = (
        select(func.count())
        .select_from(LECSHost)
        .where(LECSHost.user_id == user_id, LECSHost.deleted_at.is_(None))
    )
    result = await db.execute(count_stmt)
    count = result.scalar_one()
    return count < max_hosts


async def count_user_hosts(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """Return int count of non-deleted hosts for a user."""
    count_stmt = (
        select(func.count())
        .select_from(LECSHost)
        .where(LECSHost.user_id == user_id, LECSHost.deleted_at.is_(None))
    )
    result = await db.execute(count_stmt)
    return result.scalar_one()


async def hostname_exists(db: AsyncSession, user_id: uuid.UUID, hostname: str) -> bool:
    q = select(func.count()).select_from(LECSHost).where(
        LECSHost.user_id == user_id,
        LECSHost.hostname == hostname,
        LECSHost.deleted_at.is_(None),
    )
    result = await db.execute(q)
    return (result.scalar() or 0) > 0
