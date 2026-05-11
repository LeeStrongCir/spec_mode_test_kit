from app.api.auth import router as auth_router
from app.api.lecs_host import router as lecs_host_router
from app.api.login_record import router as login_record_router

__all__ = ["auth_router", "lecs_host_router", "login_record_router"]
