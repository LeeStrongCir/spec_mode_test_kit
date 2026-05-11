from app.security.jwt import create_access_token, create_refresh_token, decode_token, verify_token_type


def test_access_token_creation():
    token = create_access_token(subject="test-user")
    assert isinstance(token, str)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "test-user"
    assert payload["typ"] == "access"
    assert "jti" in payload
    assert "exp" in payload


def test_refresh_token_creation():
    token = create_refresh_token(subject="test-user")
    payload = decode_token(token)
    assert payload is not None
    assert payload["typ"] == "refresh"
    assert "jti" in payload


def test_decode_invalid_token():
    result = decode_token("invalid.token.here")
    assert result is None


def test_verify_token_type_access():
    token = create_access_token(subject="test-user")
    assert verify_token_type(token, "access") is True
    assert verify_token_type(token, "refresh") is False


def test_verify_token_type_refresh():
    token = create_refresh_token(subject="test-user")
    assert verify_token_type(token, "refresh") is True
    assert verify_token_type(token, "access") is False
