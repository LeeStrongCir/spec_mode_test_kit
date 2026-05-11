import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.config import settings
from app.middleware.login_logger import extract_login_info
from app.models.session import Session
from app.models.user import UserStatus
from app.schemas.auth import (
    ErrorResponse,
    LoginRequest,
    LoginResponse,
)
from app.services.auth_service import authenticate_user, create_session
from app.services.login_record_service import create_login_record

router = APIRouter(prefix="/api/auth", tags=["auth"])

MAX_AGE_ACCESS = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
MAX_AGE_REFRESH = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, remember_me: bool = False):
    refresh_max = 30 * 86400 if remember_me else settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=MAX_AGE_ACCESS,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/api/auth/refresh",
        max_age=refresh_max,
    )


def _clear_auth_cookies(response: Response):
    response.set_cookie(key="access_token", value="", max_age=0, path="/")
    response.set_cookie(key="refresh_token", value="", max_age=0, path="/api/auth/refresh")


@router.post(
    "/login",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        423: {"model": ErrorResponse, "description": "Account locked"},
    },
)
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    identifier: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    remember_me: Annotated[bool, Form()] = False,
):
    is_form = identifier is not None or password is not None
    tmpl = Jinja2Templates(directory="frontend/templates")

    if is_form:
        if not identifier or not password:
            return tmpl.TemplateResponse(
                request, "login.html",
                context={"error": "请输入用户名和密码", "identifier": identifier or ""},
                status_code=422,
            )

        info = await extract_login_info(request)
        try:
            user = await authenticate_user(identifier, password, db)
        except ValueError as e:
            code = str(e)
            msg = "账号已锁定，请稍后再试" if code == "ACCOUNT_LOCKED" else "用户名或密码错误"
            await create_login_record(
                db=db, user_id=None, status="failed", failure_reason=code,
                ip_address=info["ip_address"], user_agent=info["user_agent"],
            )
            return tmpl.TemplateResponse(
                request, "login.html", context={"error": msg, "identifier": identifier}, status_code=401,
            )

        await create_login_record(
            db=db, user_id=user.id, status="success",
            ip_address=info["ip_address"], user_agent=info["user_agent"],
        )
        user.last_login_at = datetime.now(timezone.utc)
        user.failed_login_count = 0
        await db.commit()

        access_token, refresh_token = await create_session(user, db, remember_me)
        redirect_resp = RedirectResponse(url="/console", status_code=302)
        # Set cookies directly on the redirect response (not on `response: Response`)
        redirect_resp.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax", path="/", max_age=MAX_AGE_ACCESS)
        refresh_max = 30 * 86400 if remember_me else settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
        redirect_resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax", path="/api/auth/refresh", max_age=refresh_max)
        return redirect_resp

    # JSON-based login (existing API)
    from pydantic import BaseModel

    class BodyData(BaseModel):
        identifier: str
        password: str
        remember_me: bool = False

    try:
        body = BodyData.model_validate(request.json())
    except Exception:
        return ErrorResponse(status="error", message="请求体格式错误")

    req_info = await extract_login_info(request)
    try:
        jwt_user = await authenticate_user(body.identifier, body.password, db)
    except ValueError as e:
        code = str(e)
        await create_login_record(
            db=db, user_id=None, status="failed", failure_reason=code,
            ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
        )
        if code == "ACCOUNT_LOCKED":
            return ErrorResponse(status="error", error_code="ACCOUNT_LOCKED", message="账号已锁定，请稍后再试")
        return ErrorResponse(status="error", error_code="INVALID_CREDENTIALS", message="用户名或密码错误")

    await create_login_record(
        db=db, user_id=jwt_user.id, status="success",
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    jwt_user.last_login_at = datetime.now(timezone.utc)
    jwt_user.failed_login_count = 0
    await db.commit()

    at, rt = await create_session(jwt_user, db, body.remember_me)
    _set_auth_cookies(response, at, rt, body.remember_me)
    return LoginResponse(
        message="登录成功",
        user={"id": str(jwt_user.id), "username": jwt_user.username, "email": jwt_user.email},
    )


@router.post("/logout", responses={401: {"model": ErrorResponse}})
async def logout(
    request: Request,
    response: Response,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    info = await extract_login_info(request)
    result = await db.execute(select(Session).where(Session.user_id == user.id, not Session.revoked))
    sessions = result.scalars().all()
    for s in sessions:
        s.revoked = True
        s.revoked_at = datetime.now(timezone.utc)
    await db.commit()

    await create_login_record(
        db=db,
        user_id=user.id,
        status="success",
        ip_address=info["ip_address"],
        user_agent=info["user_agent"],
    )

    _clear_auth_cookies(response)
    return {"status": "success", "message": "已登出"}


@router.post("/refresh", responses={401: {"model": ErrorResponse}})
async def refresh(
    response: Response,
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
):
    from app.security.jwt import create_access_token, create_refresh_token, decode_token

    if refresh_token_cookie is None:
        return ErrorResponse(
            status="error",
            error_code="MISSING_TOKEN",
            message="缺少刷新令牌",
        )

    payload = decode_token(refresh_token_cookie)
    if payload is None or payload.get("typ") != "refresh":
        return ErrorResponse(
            status="error",
            error_code="INVALID_TOKEN",
            message="无效的刷新令牌",
        )

    refresh_hash = hashlib.sha256(refresh_token_cookie.encode()).hexdigest()
    result = await db.execute(
        select(Session).where(
            Session.refresh_token_hash == refresh_hash,
            not Session.revoked,
        )
    )
    session = result.scalars().first()

    if session is None or session.refresh_token_expires_at < datetime.now(timezone.utc):
        return ErrorResponse(
            status="error",
            error_code="TOKEN_EXPIRED",
            message="令牌已过期",
        )

    access_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_days = 30
    refresh_expires = timedelta(days=refresh_days)

    new_access_token = create_access_token(subject=str(session.user_id), expires_delta=access_expires)
    new_refresh_token = create_refresh_token(subject=str(session.user_id), expires_delta=refresh_expires)

    session.refresh_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
    session.access_token_jti = decode_token(new_access_token)["jti"]
    session.access_token_expires_at = datetime.now(timezone.utc) + access_expires
    session.refresh_token_expires_at = datetime.now(timezone.utc) + refresh_expires
    session.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    _set_auth_cookies(response, new_access_token, new_refresh_token)

    return {"status": "success", "message": "令牌已刷新"}


@router.get("/me", responses={401: {"model": ErrorResponse}})
async def me(user=Depends(get_current_user)):
    return {
        "status": "success",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
        },
    }
