import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.session import Session
from app.models.user import User, UserStatus
from app.security.jwt import create_access_token, create_refresh_token
from app.services.password_service import verify_password


async def authenticate_user(identifier: str, password: str, db: AsyncSession) -> dict:
    """Authenticate user by username or email. Returns User dict or raises ValueError."""
    from sqlalchemy import or_

    result = await db.execute(select(User).where(or_(User.username == identifier, User.email == identifier)))
    user = result.scalars().first()

    if user is None:
        raise ValueError("INVALID_CREDENTIALS")

    if user.status == UserStatus.locked:
        raise ValueError("ACCOUNT_LOCKED")

    if user.status == UserStatus.disabled:
        raise ValueError("ACCOUNT_DISABLED")

    if not verify_password(password, user.password_hash):
        raise ValueError("INVALID_CREDENTIALS")

    return user


async def create_session(user: User, db: AsyncSession, remember_me: bool = False) -> tuple[str, str]:
    """Create access + refresh tokens, store session in DB. Returns (access_token, refresh_token)."""
    access_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_days = 30 if remember_me else settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    refresh_expires = timedelta(days=refresh_days)

    access_token = create_access_token(subject=str(user.id), expires_delta=access_expires)
    refresh_token = create_refresh_token(subject=str(user.id), expires_delta=refresh_expires)

    # Extract JTI from access token
    from app.security.jwt import decode_token

    access_payload = decode_token(access_token)
    access_jti = access_payload["jti"] if access_payload else str(uuid.uuid4())

    # Store refresh token hash
    refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    session_record = Session(
        user_id=user.id,
        access_token_jti=access_jti,
        refresh_token_hash=refresh_hash,
        access_token_expires_at=datetime.now(timezone.utc) + access_expires,
        refresh_token_expires_at=datetime.now(timezone.utc) + refresh_expires,
    )
    db.add(session_record)
    await db.commit()

    return access_token, refresh_token
