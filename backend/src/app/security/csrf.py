from fastapi_csrf_protect import CsrfProtect


def get_csrf_config():
    """Default CSRF configuration."""
    return {
        "secret_key": "change-me-csrf-secret",  # Should come from settings in production
        "max_age": 3600,  # 1 hour
        "https_only": False,  # Set True in production
        "samesite": "lax",
    }


def get_csrf_protect() -> CsrfProtect:
    csrf = CsrfProtect()
    return csrf
