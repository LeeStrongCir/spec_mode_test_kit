from fastapi import Request


async def extract_login_info(request: Request) -> dict:
    client_host = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "")
    return {
        "ip_address": client_host,
        "user_agent": user_agent,
    }
