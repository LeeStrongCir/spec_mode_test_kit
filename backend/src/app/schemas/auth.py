from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    identifier: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    status: str = "success"
    message: str = "登录成功"
    user: Optional[dict] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str


class TokenLockedResponse(BaseModel):
    status: str = "error"
    error_code: str = "ACCOUNT_LOCKED"
    message: str
    unlock_at: Optional[str] = None


class TokenRefreshedResponse(BaseModel):
    status: str = "success"
    message: str = "令牌已刷新"


class TokenLogoutResponse(BaseModel):
    status: str = "success"
    message: str = "已登出"


class UserMeResponse(BaseModel):
    status: str = "success"
    user: dict
