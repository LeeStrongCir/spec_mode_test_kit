from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db as _get_db
from app.models.user import UserStatus
from app.security.jwt import decode_token


async def get_db():
    async for session in _get_db():
        yield session


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from sqlalchemy import select

    from app.models.user import User

    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")

    payload = decode_token(access_token)
    if payload is None or payload.get("sub") is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")

    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(payload["sub"])))
    user = result.scalars().first()
    if user is None or user.status != UserStatus.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


class RedirectToLogin(Exception):
    """Custom exception that redirects unauthenticated browser users to the login page."""
    def __init__(self, redirect_url: str = "/login"):
        self.redirect_url = redirect_url


async def get_current_user_optional(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Return user dict if authenticated, None otherwise — never raises."""
    from sqlalchemy import select
    from app.models.user import User

    if access_token is None:
        return None
    payload = decode_token(access_token)
    if payload is None or payload.get("sub") is None:
        return None
    try:
        from uuid import UUID
        result = await db.execute(select(User).where(User.id == UUID(payload["sub"])))
        user = result.scalars().first()
        if user is None or user.status != UserStatus.active:
            return None
        return user
    except Exception:
        return None


async def require_auth(request: Request, user=Depends(get_current_user_optional)) -> dict:
    """Dependency for SSR page routes — redirects to /login instead of returning JSON 401."""
    if user is None:
        raise RedirectToLogin(f"/login?next={request.url.path}")
    return user


async def get_current_admin_user(user=Depends(get_current_user)):
    if user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user
