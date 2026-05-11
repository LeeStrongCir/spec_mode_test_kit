#!/usr/bin/env python3
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.api.auth import router as auth_router
from app.api.deps import RedirectToLogin, require_auth
from app.api.lecs_host import router as lecs_host_router
from app.api.login_record import router as login_record_router

logger = logging.getLogger(__name__)


async def _reset_stuck_hosts():
    from datetime import datetime, timezone

    from sqlalchemy import select

    from app.db import async_session_factory
    from app.models.lecs_host import HostStatus, LECSHost

    transitions = {
        "creating": "failed",
        "shutting_down": "stopped",
        "starting": "failed",
        "deleting": "stopped",
    }
    async with async_session_factory() as session:
        result = await session.execute(
            select(LECSHost).where(LECSHost.status.in_(list(transitions.keys())))
        )
        stuck_hosts = result.scalars().all()
        for h in stuck_hosts:
            new_status = transitions[h.status.value if isinstance(h.status, HostStatus) else h.status]
            h.status = HostStatus(new_status)
            h.updated_at = datetime.now(timezone.utc)
        if stuck_hosts:
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from sqlalchemy import select

    from app.db import async_session_factory
    from app.models.user import User, UserStatus
    from app.services.password_service import hash_password

    async with async_session_factory() as session:
        existing_admin = await session.execute(select(User).where(User.username == "admin"))
        admin = existing_admin.scalars().first()
        if admin is None:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin@123"),
                status=UserStatus.active,
                failed_login_count=0,
            )
            session.add(admin)
            await session.commit()

    await _reset_stuck_hosts()

    yield


app = FastAPI(
    title="Lee Cloud Platform",
    version="0.2.0",
    lifespan=lifespan,
)


@app.exception_handler(RedirectToLogin)
async def redirect_handler(request: Request, exc: RedirectToLogin):
    return RedirectResponse(url=exc.redirect_url, status_code=303)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(login_record_router)
app.include_router(auth_router)
app.include_router(lecs_host_router)


@app.get("/console", response_class=HTMLResponse)
async def console_page(request: Request, user=Depends(require_auth)):
    return templates.TemplateResponse(
        request,
        "console.html",
        context={"user": user},
    )


@app.get("/console-full", response_class=HTMLResponse)
async def console_full_page(request: Request, user=Depends(require_auth)):
    return templates.TemplateResponse(
        request,
        "console-full.html",
        context={"user": user},
    )


@app.get("/console/lecs-hosts/list", response_class=HTMLResponse)
async def lecs_host_list_page(request: Request, user=Depends(require_auth)):
    return templates.TemplateResponse(
        request,
        "lecs_host_list.html",
        context={"user": user},
    )


@app.get("/console/lecs-hosts/create", response_class=HTMLResponse)
async def lecs_host_create_page(request: Request, user=Depends(require_auth)):
    return templates.TemplateResponse(
        request,
        "lecs_host_create.html",
        context={"user": user},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/login-history", response_class=HTMLResponse)
async def login_history_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login_history.html",
        context={
            "records": [],
            "pagination": {"total_pages": 0, "page": 1},
        },
    )


@app.get("/admin/login-records", response_class=HTMLResponse)
async def admin_login_records_page(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/login_records.html",
        context={
            "records": [],
            "pagination": {"total_pages": 0, "page": 1},
            "start_time": "",
            "end_time": "",
            "ip_address": "",
            "status_filter": "all",
        },
    )
