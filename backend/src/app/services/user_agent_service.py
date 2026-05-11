import re


def parse_user_agent(user_agent_string: str) -> dict:
    if not user_agent_string:
        return {"device_type": "unknown", "browser": "unknown", "operating_system": "unknown"}

    s = user_agent_string

    if re.search(r"Mobile|Android|iPhone|iPad|iPod", s, re.I):
        device_type = "mobile" if re.search(r"Mobile|iPhone|Android", s, re.I) else "tablet"
    else:
        device_type = "desktop"

    browser = "unknown"
    if "Edg/" in s:
        browser = "Edge"
    elif "Chrome/" in s:
        browser = "Chrome"
    elif "Firefox/" in s:
        browser = "Firefox"
    elif "Safari/" in s and "Chrome" not in s:
        browser = "Safari"
    elif "Opera" in s or "OPR/" in s:
        browser = "Opera"

    os_name = "unknown"
    if "Windows" in s:
        os_name = "Windows"
    elif "Mac OS X" in s or "Macintosh" in s:
        os_name = "macOS"
    elif "iPhone" in s or "iPad" in s:
        os_name = "iOS"
    elif "Android" in s:
        os_name = "Android"
    elif "Linux" in s:
        os_name = "Linux"

    return {
        "device_type": device_type,
        "browser": browser,
        "operating_system": os_name,
    }
