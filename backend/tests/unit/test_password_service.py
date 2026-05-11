from app.services.password_service import hash_password, needs_rehash, verify_password


def test_hash_password_returns_string():
    h = hash_password("mysecret")
    assert isinstance(h, str)
    assert len(h) > 10  # Argon2 hash is long


def test_verify_password_correct():
    h = hash_password("mysecret")
    assert verify_password("mysecret", h) is True


def test_verify_password_wrong():
    h = hash_password("mysecret")
    assert verify_password("wrongpassword", h) is False


def test_needs_rehash_initially_false():
    h = hash_password("mysecret")
    assert needs_rehash(h) is False
