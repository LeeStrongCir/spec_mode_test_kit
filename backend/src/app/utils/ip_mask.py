def mask_ip(ip_address: str) -> str:
    """Mask IP address for privacy display."""
    if not ip_address or ip_address == "0.0.0.0":
        return "●●"
    parts = ip_address.split(".")
    if len(parts) == 4:  # IPv4
        parts[2] = "●"
        parts[3] = "●"
        return ".".join(parts)
    # IPv6 - mask last 80 bits
    return ip_address[:8] + ":" + "●" * 4
