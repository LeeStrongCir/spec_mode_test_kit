from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_record import LoginRecord, LoginStatus
from app.services.user_agent_service import parse_user_agent


async def create_login_record(
    db: AsyncSession,
    user_id=None,
    status: str = "success",
    ip_address: str = "0.0.0.0",
    user_agent: str = "",
    request=None,
    is_anomalous: bool = False,
    ip_geo_location: str = None,
    failure_reason: str = None,
):
    ua_info = parse_user_agent(user_agent or "")

    record = LoginRecord(
        user_id=user_id,
        login_time=datetime.now(timezone.utc),
        ip_address=ip_address,
        device_type=ua_info["device_type"],
        browser=ua_info["browser"],
        operating_system=ua_info["operating_system"],
        status=LoginStatus(status),
        failure_reason=failure_reason,
        is_anomalous=is_anomalous,
        ip_geo_location=ip_geo_location,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def check_anomalous_login(db: AsyncSession, user_id) -> bool:
    result = await db.execute(
        select(LoginRecord.ip_address)
        .where(LoginRecord.user_id == user_id, LoginRecord.status == LoginStatus.success)
        .order_by(desc(LoginRecord.login_time))
        .limit(10)
    )
    recent_ips = result.scalars().all()

    if len(recent_ips) == 0:
        return False

    return True
