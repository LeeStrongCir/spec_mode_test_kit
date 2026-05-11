import re
from typing import Optional

# --- Hostname validation ---
_HOSTNAME_RE = re.compile(r"^[\w]{4,10}$")
_HOSTNAME_ERR = "主机名仅支持英文、数字、下划线，长度4-10字符，不可以下划线开头"


def validate_hostname(hostname: str) -> tuple[bool, Optional[str]]:
    """Validate hostname: 4-10 word chars, no leading underscore."""
    if not hostname or hostname.startswith("_"):
        return False, _HOSTNAME_ERR
    if not _HOSTNAME_RE.match(hostname):
        return False, _HOSTNAME_ERR
    return True, None


# --- Username validation ---
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_@.+\\-]{4,16}$")
_USERNAME_ERR = "用户名长度4-16字符"


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """Validate username: 4-16 chars, alphanumeric plus @.+-. """
    if not username or not _USERNAME_RE.match(username):
        return False, _USERNAME_ERR
    return True, None


# --- Password validation ---
_PASSWORD_RE = re.compile(r"^[a-zA-Z0-9_@#$%^&+=!\\-]{8,32}$")
_PASSWORD_ERR = "密码长度8-32字符"


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Validate password: 8-32 chars from allowed set."""
    if not password or not _PASSWORD_RE.match(password):
        return False, _PASSWORD_ERR
    return True, None


# --- IP address validation ---
_IPV4_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$"
)
_IP_ERR = "请输入有效的IP地址"


def validate_ip_address(ip: str) -> tuple[bool, Optional[str]]:
    """Validate IPv4 address."""
    if not ip or not _IPV4_RE.match(ip):
        return False, _IP_ERR
    return True, None


# --- IP mask validation ---
_MASK_ERR = "请选择有效的掩码值"


def validate_ip_mask(mask: int) -> tuple[bool, Optional[str]]:
    """Validate subnet mask: integer 8-24."""
    if not isinstance(mask, int) or mask < 8 or mask > 24:
        return False, _MASK_ERR
    return True, None


# --- Duration validation ---
_VALID_DURATIONS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 24}
_DURATION_ERR = "请选择有效的购买时长"


def validate_duration(duration: int) -> tuple[bool, Optional[str]]:
    """Validate duration: 1-9, 12, or 24 months."""
    if duration not in _VALID_DURATIONS:
        return False, _DURATION_ERR
    return True, None


# --- Spec ID validation ---
_SPEC_ERR = "请选择有效的实例规格"


def validate_spec_id(spec_id: str, valid_specs: set[str]) -> tuple[bool, Optional[str]]:
    """Validate spec_id against a set of valid spec IDs."""
    if spec_id not in valid_specs:
        return False, _SPEC_ERR
    return True, None
