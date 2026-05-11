import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db import async_session_factory
from app.models.lecs_host import HostStatus, LECSHost

logger = logging.getLogger(__name__)

STATE_TRANSITIONS: dict[str, dict[str, str]] = {
    "normal": {"shutdown": "shutting_down"},
    "failed": {"start": "starting", "delete": "deleting"},
    "stopped": {"start": "starting", "delete": "deleting"},
}

LOCKED_STATES = {"creating", "shutting_down", "starting", "deleting"}

_active_tasks: dict[uuid.UUID, asyncio.Task] = {}


def validate_transition(current_status: str, operation: str) -> tuple[bool, Optional[str]]:
    allowed_ops = STATE_TRANSITIONS.get(current_status, {})
    if operation in allowed_ops:
        return True, allowed_ops[operation]
    return False, None


def track_active_tasks() -> dict[uuid.UUID, asyncio.Task]:
    return _active_tasks


def cancel_task(host_id: uuid.UUID) -> bool:
    task = _active_tasks.get(host_id)
    if task and not task.done():
        task.cancel()
        _active_tasks.pop(host_id, None)
        return True
    return False


def _register_task(host_id: uuid.UUID, task: asyncio.Task) -> None:
    _active_tasks[host_id] = task


def _unregister_task(host_id: uuid.UUID) -> None:
    _active_tasks.pop(host_id, None)


async def create_background_task(
    db: AsyncSession,
    session_factory: async_sessionmaker,
    host_id: uuid.UUID,
    task_type: str,
    duration_seconds: int,
    user_id: Optional[uuid.UUID] = None,
) -> None:
    async def _worker() -> None:
        try:
            logger.info(
                "lifecycle: type=%s host_id=%s user_id=%s started",
                task_type, host_id, user_id,
            )
            await asyncio.sleep(duration_seconds)

            async with session_factory() as session:
                result = await session.execute(
                    select(LECSHost).where(LECSHost.id == host_id)
                )
                host = result.scalars().first()
                if host is None:
                    logger.warning("lifecycle: host_id=%s not found during %s", host_id, task_type)
                    return

                if task_type == "create":
                    host.status = HostStatus.normal
                elif task_type == "shutdown":
                    host.status = HostStatus.stopped
                elif task_type == "start":
                    host.status = HostStatus.normal
                elif task_type == "delete":
                    host.deleted_at = datetime.now(timezone.utc)
                    host.status = HostStatus.deleted
                else:
                    host.status = HostStatus.failed

                host.updated_at = datetime.now(timezone.utc)
                await session.commit()

                logger.info(
                    "lifecycle: type=%s host_id=%s user_id=%s completed status=%s",
                    task_type, host_id, user_id, host.status.value,
                )
        except asyncio.CancelledError:
            logger.info("lifecycle: type=%s host_id=%s cancelled", task_type, host_id)
            raise
        except Exception:
            logger.exception(
                "lifecycle: type=%s host_id=%s user_id=%s failed",
                task_type, host_id, user_id,
            )
            async with session_factory() as session:
                result = await session.execute(
                    select(LECSHost).where(LECSHost.id == host_id)
                )
                host = result.scalars().first()
                if host and task_type == "create":
                    host.status = HostStatus.failed
                    host.updated_at = datetime.now(timezone.utc)
                    await session.commit()
        finally:
            _unregister_task(host_id)

    task = asyncio.create_task(_worker())
    _register_task(host_id, task)


def _log_operation(host_id, user_id, action, details=""):
    logger.info("LECS %s: host_id=%s, user_id=%s %s", action, host_id, user_id, details)


def spawn_shutdown_task(host_id, factory, user_id):
    _log_operation(host_id, user_id, "shutdown", "spawned")
    return create_background_task(None, factory, host_id, "shutdown", 10, user_id)


def spawn_start_task(host_id, factory, user_id):
    _log_operation(host_id, user_id, "start", "spawned")
    return create_background_task(None, factory, host_id, "start", 10, user_id)


def spawn_delete_task(host_id, factory, user_id):
    _log_operation(host_id, user_id, "delete", "spawned")
    return create_background_task(None, factory, host_id, "delete", 5, user_id)
