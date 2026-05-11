import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db import async_session_factory
from app.models.lecs_host import HostStatus, LECSHost
from app.schemas.lecs_host import (
    INSTANCE_SPECS,
    CreateHostRequest,
    SpecCategory,
    SpecItem,
)
from app.services.lecs_host_service import (
    check_quota,
    create_host,
    get_host_by_id,
    hostname_exists,
    list_hosts,
)
from app.services.lecs_lifecycle_service import (
    _active_tasks,
    spawn_delete_task,
    spawn_shutdown_task,
    spawn_start_task,
)
from app.services.lecs_lifecycle_service import (
    async_session_factory as lifecycle_session_factory,
)

router = APIRouter(prefix="/api/v1/lecs-hosts", tags=["lecs-hosts"])


def _is_admin(user) -> bool:
    return user.username == "admin"


@router.get("/pricing")
async def get_pricing(user=Depends(get_current_user)):
    economy = [
        SpecItem(**v)
        for v in INSTANCE_SPECS.values()
        if v["instance_type"] == "economy"
    ]
    high_perf = [
        SpecItem(**v)
        for v in INSTANCE_SPECS.values()
        if v["instance_type"] == "high_performance"
    ]
    return {
        "status": "success",
        "data": SpecCategory(economy=economy, high_performance=high_perf),
    }


@router.get("")
async def list_lecs_hosts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await list_hosts(db, user, page, page_size, _is_admin(user))
    return {"status": "success", "data": result.model_dump()}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_lecs_host(
    body: CreateHostRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not await check_quota(db, current_user.id):
        raise HTTPException(
            status_code=403,
            detail={
                "status": "error",
                "error_code": "QUOTA_EXCEEDED",
                "message": "主机数量达到上限",
            },
        )
    if await hostname_exists(db, current_user.id, body.hostname):
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "主机名已存在"},
        )
    if body.spec_id not in INSTANCE_SPECS:
        raise HTTPException(status_code=422, detail="Invalid spec_id")

    spec = INSTANCE_SPECS[body.spec_id]
    if body.billing_mode == "subscription":
        total = spec["monthly_price"] * body.duration
        display = f"{total}/月"
    else:
        daily = spec["monthly_price"] / 30
        total = daily * body.duration
        display = f"{daily:.2f}/天"

    cost = {
        "billing_mode": body.billing_mode,
        "unit_price": spec["monthly_price"],
        "duration": body.duration,
        "total": total,
        "currency": "CNY",
        "display": display,
    }

    host = await create_host(db, current_user, body, cost)

    async def _create_worker():
        try:
            await asyncio.sleep(30)
            async with lifecycle_session_factory() as s:
                await s.execute(
                    update(LECSHost)
                    .where(LECSHost.id == host.id)
                    .values(status=HostStatus.normal, updated_at=datetime.now(timezone.utc))
                )
                await s.commit()
        except asyncio.CancelledError:
            pass
        except Exception:
            async with lifecycle_session_factory() as s:
                await s.execute(
                    update(LECSHost)
                    .where(LECSHost.id == host.id)
                    .values(
                        status=HostStatus.failed,
                        error_msg="Task execution failed",
                        updated_at=datetime.now(timezone.utc),
                    )
                )
                await s.commit()
        finally:
            _active_tasks.pop(host.id, None)

    _active_tasks[host.id] = asyncio.create_task(_create_worker())

    return {
        "status": "success",
        "data": {
            "id": str(host.id),
            "hostname": host.hostname,
            "status": "creating",
            "message": "任务已提交",
        },
    }


@router.post("/{host_id}/shutdown")
async def shutdown_host(
    host_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    host = await get_host_by_id(db, host_id, user, _is_admin(user))
    if host is None:
        raise HTTPException(status_code=404, detail="主机不存在")
    if host.status != HostStatus.normal:
        raise HTTPException(
            status_code=409,
            detail={
                "status": "error",
                "error_code": "INVALID_STATE",
                "message": "仅可对运行中的主机执行关机操作",
            },
        )
    host.status = HostStatus.shutting_down
    host.updated_at = datetime.now(timezone.utc)
    await db.commit()
    spawn_shutdown_task(host.id, async_session_factory, user.id)
    return {
        "status": "success",
        "data": {
            "id": str(host.id),
            "status": "shutting_down",
            "message": "关机指令已下发",
        },
    }


@router.post("/{host_id}/start")
async def start_host(
    host_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    host = await get_host_by_id(db, host_id, user, _is_admin(user))
    if host is None:
        raise HTTPException(status_code=404, detail="主机不存在")
    if host.status not in (HostStatus.stopped, HostStatus.failed):
        raise HTTPException(
            status_code=409,
            detail={
                "status": "error",
                "error_code": "INVALID_STATE",
                "message": "仅可对已关机或创建失败的主机执行启动操作",
            },
        )
    host.status = HostStatus.starting
    host.updated_at = datetime.now(timezone.utc)
    await db.commit()
    spawn_start_task(host.id, async_session_factory, user.id)
    return {
        "status": "success",
        "data": {
            "id": str(host.id),
            "status": "starting",
            "message": "启动指令已下发",
        },
    }


@router.delete("/{host_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_host(
    host_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    host = await get_host_by_id(db, host_id, user, _is_admin(user))
    if host is None:
        raise HTTPException(status_code=404, detail="主机不存在")
    if host.status not in (HostStatus.stopped, HostStatus.failed):
        raise HTTPException(
            status_code=403,
            detail={
                "status": "error",
                "error_code": "NOT_STOPPED",
                "message": "仅支持对已关机或创建失败的主机执行删除",
            },
        )
    host.status = HostStatus.deleting
    host.updated_at = datetime.now(timezone.utc)
    await db.commit()
    spawn_delete_task(host.id, async_session_factory, user.id)
    return {
        "status": "success",
        "data": {
            "id": str(host.id),
            "status": "deleting",
            "message": "删除中，请等待处理完成",
        },
    }
