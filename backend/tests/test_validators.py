from app.utils.validators import (
    validate_duration,
    validate_hostname,
    validate_ip_address,
    validate_ip_mask,
    validate_password,
    validate_username,
)


def test_hostname_valid():
    ok, err = validate_hostname("test123")
    assert ok is True
    assert err is None


def test_hostname_underscores():
    ok, err = validate_hostname("te_st1")
    assert ok is True


def test_hostname_too_short():
    ok, err = validate_hostname("abc")
    assert ok is False
    assert err is not None


def test_hostname_starts_underscore():
    ok, err = validate_hostname("_test")
    assert ok is False


def test_hostname_too_long():
    ok, err = validate_hostname("toolongname1")
    assert ok is False


def test_username_valid():
    ok, err = validate_username("usr1")
    assert ok is True


def test_username_too_short():
    ok, err = validate_username("ab")
    assert ok is False


def test_username_too_long():
    ok, err = validate_username("a" * 17)
    assert ok is False


def test_password_valid():
    ok, err = validate_password("Str0ng!Pass")
    assert ok is True


def test_password_too_short():
    ok, err = validate_password("Ab1!")
    assert ok is False


def test_password_too_long():
    ok, err = validate_password("a" * 33)
    assert ok is False


def test_ip_valid():
    ok, err = validate_ip_address("192.168.1.100")
    assert ok is True


def test_ip_invalid():
    ok, err = validate_ip_address("999.999.999.999")
    assert ok is False


def test_ip_not_number():
    ok, err = validate_ip_address("abc.def.ghi.jkl")
    assert ok is False


def test_mask_valid_8():
    ok, err = validate_ip_mask(8)
    assert ok is True


def test_mask_valid_24():
    ok, err = validate_ip_mask(24)
    assert ok is True


def test_mask_too_low():
    ok, err = validate_ip_mask(7)
    assert ok is False


def test_mask_too_high():
    ok, err = validate_ip_mask(25)
    assert ok is False


def test_duration_1_to_9():
    for d in range(1, 10):
        ok, err = validate_duration(d)
        assert ok is True, f"duration {d} should be valid"


def test_duration_12():
    ok, err = validate_duration(12)
    assert ok is True


def test_duration_24():
    ok, err = validate_duration(24)
    assert ok is True


def test_duration_invalid_10():
    ok, err = validate_duration(10)
    assert ok is False


def test_duration_invalid_13():
    ok, err = validate_duration(13)
    assert ok is False
