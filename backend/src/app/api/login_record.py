import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.login_record import LoginRecordResponse
from app.utils.ip_mask import mask_ip

router = APIRouter(prefix="/api", tags=["login-records"])


def build_login_record_query(start_time=None, end_time=None, ip_address=None):
    """Build filter conditions for login record queries."""
    conditions = []
    from app.models.login_record import LoginRecord

    if start_time:
        conditions.append(LoginRecord.login_time >= start_time)
    if end_time:
        conditions.append(LoginRecord.login_time <= end_time)
    if ip_address:
        conditions.append(LoginRecord.ip_address == ip_address)
    return conditions


@router.get("/auth/login-history")
async def get_login_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status_filter: str = Query("all", alias="status"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get current user's login history with pagination."""
    from app.models.login_record import LoginRecord, LoginStatus

    query = select(LoginRecord).where(LoginRecord.user_id == user.id)
    if status_filter and status_filter != "all":
        query = query.where(LoginRecord.status == LoginStatus(status_filter))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(desc(LoginRecord.login_time))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    records = result.scalars().all()

    records_response = []
    for r in records:
        records_response.append(
            LoginRecordResponse(
                id=str(r.id),
                login_time=r.login_time,
                ip_address=mask_ip(r.ip_address),
                device_type=r.device_type,
                browser=r.browser,
                operating_system=r.operating_system,
                status=r.status.value,
                is_anomalous=r.is_anomalous,
            )
        )

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    return {
        "status": "success",
        "records": records_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    }


@router.get("/admin/login-records")
async def get_admin_login_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_time: str = Query(None),
    end_time: str = Query(None),
    ip_address: str = Query(None),
    status_filter: str = Query("all", alias="status"),
    is_anomalous: bool = Query(None),
    db: AsyncSession = Depends(get_db),
    admin_user=Depends(get_current_user),
):
    """Get all login records (admin only)."""
    from app.models.login_record import LoginRecord, LoginStatus
    from app.models.user import User

    if admin_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )

    query = select(LoginRecord, User).join(User, LoginRecord.user_id == User.id, isouter=True)

    if status_filter and status_filter != "all":
        query = query.where(LoginRecord.status == LoginStatus(status_filter))
    if is_anomalous is not None:
        query = query.where(LoginRecord.is_anomalous == is_anomalous)

    conditions = build_login_record_query(
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        ip_address=ip_address,
    )
    for cond in conditions:
        query = query.where(cond)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(desc(LoginRecord.login_time))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    records_response = []
    for login_record, user in rows:
        records_response.append(
            {
                "id": str(login_record.id),
                "user_id": str(user.id) if user else None,
                "username": user.username if user else None,
                "email": user.email if user else None,
                "login_time": login_record.login_time,
                "ip_address": login_record.ip_address,
                "ip_geo_location": login_record.ip_geo_location,
                "device_type": login_record.device_type,
                "browser": login_record.browser,
                "operating_system": login_record.operating_system,
                "status": login_record.status.value,
                "failure_reason": login_record.failure_reason,
                "is_anomalous": login_record.is_anomalous,
            }
        )

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    return {
        "status": "success",
        "records": records_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    }
