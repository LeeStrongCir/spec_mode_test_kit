from app.services.user_agent_service import parse_user_agent


def test_parse_chrome_windows():
    ua = (  # noqa: E501
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    result = parse_user_agent(ua)
    assert result["device_type"] == "desktop"
    assert result["browser"] == "Chrome"
    assert result["operating_system"] == "Windows"


def test_parse_safari_macos():
    ua = (  # noqa: E501
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15"
        " (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    )
    result = parse_user_agent(ua)
    assert result["device_type"] == "desktop"
    assert result["browser"] == "Safari"
    assert result["operating_system"] == "macOS"


def test_parse_chrome_android():
    ua = (  # noqa: E501
        "Mozilla/5.0 (Linux; Android 14; SM-S908B) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    )
    result = parse_user_agent(ua)
    assert result["device_type"] == "mobile"
    assert result["browser"] == "Chrome"
    assert result["operating_system"] == "Android"


def test_parse_empty_ua():
    result = parse_user_agent("")
    assert result["device_type"] == "unknown"
    assert result["browser"] == "unknown"
    assert result["operating_system"] == "unknown"


def test_parse_firefox_linux():
    ua = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    result = parse_user_agent(ua)
    assert result["device_type"] == "desktop"
    assert result["browser"] == "Firefox"
    assert result["operating_system"] == "Linux"
