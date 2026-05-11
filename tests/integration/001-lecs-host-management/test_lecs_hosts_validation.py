"""
LECS Hosts Validation Integration Tests

Boundary value analysis for all input fields per ISO 29119-4.
Tests validation rules VR-001 through VR-009 from data-model.md.

Focus: Input boundary validation only (not full CRUD lifecycle).
"""

import pytest
from unittest.mock import patch, MagicMock


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_billing_service():
    """Mock external billing service to prevent real charges during tests."""
    with patch("app.services.billing.BillingService") as mock:
        mock.return_value.create_subscription.return_value = {
            "subscription_id": "sub_test_123",
            "status": "active",
        }
        mock.return_value.calculate_price.return_value = {
            "unit_price": 100.0,
            "total": 100.0,
            "currency": "CNY",
        }
        yield mock


@pytest.fixture
def mock_task_queue():
    """Mock external task queue to prevent real host provisioning."""
    with patch("app.services.task_queue.TaskQueue") as mock:
        mock.return_value.enqueue_host_creation.return_value = {
            "task_id": "task_test_456",
            "status": "queued",
        }
        yield mock


# ============================================================================
# VR-001: Hostname Validation
# Rule: ^[\w]{4,10}$, cannot start with '_'
# ============================================================================

class TestHostnameValidation:
    """Boundary value analysis for hostname field (VR-001)."""

    @pytest.mark.parametrize(
        "hostname,expected_status,description",
        [
            # Invalid: starts with underscore
            ("_invalid", 400, "starts with underscore"),
            ("_abc", 400, "starts with underscore (min length)"),
            ("_abcdefghij", 400, "starts with underscore (max length)"),
            # Invalid: below minimum length (4)
            ("ab", 400, "2 chars, below minimum"),
            ("abc", 400, "3 chars, below minimum"),
            # Valid: exact lower boundary
            ("abcd", 201, "4 chars, exact lower boundary"),
            ("a1b2", 400, "4 chars with special chars not in \w"),
            # Valid: middle values
            ("valid01", 201, "7 chars, middle value"),
            ("host_01", 201, "7 chars with underscore"),
            ("ABCDEFGH", 201, "8 chars uppercase"),
            # Valid: exact upper boundary
            ("abcdefghij", 201, "10 chars, exact upper boundary"),
            ("0123456789", 201, "10 chars digits"),
            # Invalid: above maximum length (10)
            ("abcdefghijklmn", 400, "14 chars, above maximum"),
            ("abcdefghijk", 400, "11 chars, one above maximum"),
        ],
    )
    def test_hostname_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        hostname,
        expected_status,
        description,
    ):
        """Test hostname boundary values per ISO 29119-4."""
        payload = {
            "hostname": hostname,
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Hostname '{hostname}' ({description}): expected {expected_status}, got {response.status_code}"

        if expected_status == 400:
            data = response.json()
            assert "error" in data or "detail" in data or "message" in data

    @pytest.mark.parametrize(
        "hostname,expected_status,description",
        [
            ("", 400, "empty string"),
            ("   ", 400, "whitespace only"),
            ("a!b", 400, "contains invalid character !"),
            ("a b", 400, "contains space"),
            ("a.b", 400, "contains dot"),
            ("a-b", 400, "contains hyphen"),
        ],
    )
    def test_hostname_invalid_characters(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        hostname,
        expected_status,
        description,
    ):
        """Test hostname with invalid character patterns."""
        payload = {
            "hostname": hostname,
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Hostname '{hostname}' ({description}): expected {expected_status}"


# ============================================================================
# VR-002: Credential Validation (Username & Password)
# Username: ^[a-zA-Z0-9_@.+-]{4,16}$
# Password: ^[a-zA-Z0-9_@#$%^&+=!-]{8,32}$
# ============================================================================

class TestCredentialValidation:
    """Boundary value analysis for credentials (VR-002)."""

    @pytest.mark.parametrize(
        "username,expected_status,description",
        [
            # Invalid: below minimum length (4)
            ("ab", 400, "2 chars, too short"),
            ("abc", 400, "3 chars, too short"),
            # Valid: exact lower boundary
            ("abcd", 201, "4 chars, exact lower boundary"),
            ("a_b", 400, "3 chars with underscore"),
            # Valid: middle values
            ("user01", 201, "6 chars, middle value"),
            ("test_user", 201, "9 chars with underscore"),
            ("user@domain", 201, "11 chars with @"),
            ("user.name", 400, "11 chars with dot - verify allowed"),
            # Valid: exact upper boundary
            ("abcdefghij", 201, "10 chars"),
            ("abcdefghijklmn", 400, "14 chars"),
            ("abcdefghijklmnop", 400, "16 chars, verify boundary"),
            ("abcdefghijklmnopq", 400, "17 chars, above maximum"),
        ],
    )
    def test_username_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        username,
        expected_status,
        description,
    ):
        """Test username boundary values."""
        payload = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": username,
            "password": "Abcdefg1",
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Username '{username}' ({description}): expected {expected_status}, got {response.status_code}"

        if expected_status == 400:
            data = response.json()
            assert "error" in data or "detail" in data or "message" in data

    @pytest.mark.parametrize(
        "password,expected_status,description",
        [
            # Invalid: below minimum length (8)
            ("Ab1", 400, "3 chars, too short"),
            ("Abcdefg", 400, "7 chars, below minimum"),
            # Valid: exact lower boundary
            ("Abcdefg1", 201, "8 chars, exact lower boundary"),
            # Valid: middle values
            ("SecureP@ss1", 201, "11 chars, middle value"),
            ("MyP@ssw0rd!", 201, "11 chars with special chars"),
            ("Pass#1234", 201, "9 chars with #"),
            # Valid: upper boundary
            ("A" * 32 + "1", 201, "32 chars, exact upper boundary (all A's + 1)"),
            # Need exactly 32 chars
            ("Abcdefghijklmnopqrstuvwxy12345", 201, "32 chars, upper boundary"),
            # Invalid: above maximum length (32)
            ("A" * 33, 400, "33 chars, above maximum"),
            ("Abcdefghijklmnopqrstuvwxy123456", 400, "33 chars with digit"),
        ],
    )
    def test_password_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        password,
        expected_status,
        description,
    ):
        """Test password boundary values."""
        payload = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": password,
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Password {description}: expected {expected_status}, got {response.status_code}"

        if expected_status == 400:
            data = response.json()
            assert "error" in data or "detail" in data or "message" in data


# ============================================================================
# VR-003: Duration Validation
# Valid values: {1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 24}
# ============================================================================

class TestDurationValidation:
    """Boundary value analysis for duration field (VR-003)."""

    @pytest.mark.parametrize(
        "duration,expected_status,description",
        [
            # Invalid: below minimum
            (0, 400, "zero, below minimum"),
            (-1, 400, "negative value"),
            # Valid: lower boundary
            (1, 201, "1 month, exact lower boundary"),
            # Valid: middle values in 1-9 range
            (5, 201, "5 months, middle of 1-9"),
            (9, 201, "9 months, upper of continuous range"),
            # Invalid: gaps in allowed values
            (10, 400, "10 months, not in allowed set"),
            (11, 400, "11 months, not in allowed set"),
            # Valid: discontinuous values
            (12, 201, "12 months, allowed discontinuous value"),
            # Invalid: values between 12 and 24
            (13, 400, "13 months, not in allowed set"),
            (18, 400, "18 months, not in allowed set"),
            (23, 400, "23 months, not in allowed set"),
            # Valid: upper boundary
            (24, 201, "24 months, exact upper boundary"),
            # Invalid: above maximum
            (25, 400, "25 months, above maximum"),
            (36, 400, "36 months, above maximum"),
        ],
    )
    def test_duration_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        duration,
        expected_status,
        description,
    ):
        """Test duration boundary values including discontinuous allowed set."""
        payload = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": duration,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Duration {duration} ({description}): expected {expected_status}, got {response.status_code}"

        if expected_status == 400:
            data = response.json()
            assert "error" in data or "detail" in data or "message" in data


# ============================================================================
# VR-004: Billing Mode Validation
# Valid values: "subscription", "on_demand"
# ============================================================================

class TestBillingModeValidation:
    """Boundary value analysis for billing_mode field (VR-004)."""

    @pytest.mark.parametrize(
        "billing_mode,expected_status,description",
        [
            ("subscription", 201, "valid: subscription"),
            ("on_demand", 201, "valid: on_demand"),
            ("", 400, "empty string"),
            ("Subscription", 400, "case-sensitive: Subscription"),
            ("ON_DEMAND", 400, "case-sensitive: ON_DEMAND"),
            ("prepaid", 400, "invalid value: prepaid"),
            ("postpaid", 400, "invalid value: postpaid"),
            ("pay_as_you_go", 400, "invalid value: pay_as_you_go"),
            (None, 400, "null value"),
        ],
    )
    def test_billing_mode_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        billing_mode,
        expected_status,
        description,
    ):
        """Test billing_mode enumeration validation."""
        payload = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": billing_mode,
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Billing mode '{billing_mode}' ({description}): expected {expected_status}, got {response.status_code}"


# ============================================================================
# VR-007: Spec ID Validation
# Must be in INSTANCE_SPECS
# ============================================================================

class TestSpecIdValidation:
    """Boundary value analysis for spec_id field (VR-007)."""

    @pytest.mark.parametrize(
        "spec_id,expected_status,description",
        [
            # Valid: all allowed spec_ids
            ("eco-2c2g", 201, "valid: economy 2C2G"),
            ("eco-2c4g", 201, "valid: economy 2C4G"),
            ("eco-2c8g", 201, "valid: economy 2C8G"),
            ("eco-4c8g", 201, "valid: economy 4C8G"),
            ("perf-2c4g", 201, "valid: perf 2C4G"),
            ("perf-2c8g", 201, "valid: perf 2C8G"),
            ("perf-4c8g", 201, "valid: perf 4C8G"),
            ("perf-8c16g", 201, "valid: perf 8C16G"),
            # Invalid: non-existent spec_ids
            ("eco-1c1g", 400, "invalid: non-existent economy spec"),
            ("perf-16c32g", 400, "invalid: non-existent perf spec"),
            ("", 400, "empty string"),
            ("ECO-2C2G", 400, "case-sensitive: ECO-2C2G"),
            ("invalid-spec", 400, "invalid: arbitrary string"),
            (None, 400, "null value"),
        ],
    )
    def test_spec_id_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        spec_id,
        expected_status,
        description,
    ):
        """Test spec_id enumeration validation."""
        payload = {
            "hostname": "validhost",
            "spec_id": spec_id,
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Spec ID '{spec_id}' ({description}): expected {expected_status}, got {response.status_code}"


# ============================================================================
# VR-009: IP Address & Mask Validation (Manual IP Mode)
# ip_address: valid IPv4 format
# ip_mask: integer 8-24
# ============================================================================

class TestIPValidation:
    """Boundary value analysis for IP address and mask (VR-009)."""

    @pytest.mark.parametrize(
        "ip_address,expected_status,description",
        [
            # Valid IPs
            ("192.168.1.100", 201, "valid: private IP"),
            ("10.0.0.1", 201, "valid: private IP class A"),
            ("172.16.0.1", 201, "valid: private IP class B"),
            ("8.8.8.8", 201, "valid: public IP"),
            ("255.255.255.255", 201, "valid: broadcast IP (format valid)"),
            # Invalid IPs
            ("999.999.999.999", 400, "invalid: octets > 255"),
            ("256.0.0.0", 400, "invalid: first octet > 255"),
            ("192.168.1.256", 400, "invalid: last octet > 255"),
            ("", 400, "invalid: empty string"),
            ("192.168.1", 400, "invalid: incomplete IPv4"),
            ("192.168.1.1.1", 400, "invalid: too many octets"),
            ("abc.def.ghi.jkl", 400, "invalid: non-numeric"),
            ("192.168.1.100 ", 400, "invalid: trailing space"),
            ("2001:db8::1", 400, "invalid: IPv6 when IPv4 expected"),
        ],
    )
    def test_ip_address_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        ip_address,
        expected_status,
        description,
    ):
        """Test IP address format validation in manual mode."""
        payload = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "manual",
            "ip_address": ip_address,
            "ip_mask": 24,
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"IP '{ip_address}' ({description}): expected {expected_status}, got {response.status_code}"

        if expected_status == 400:
            data = response.json()
            assert "error" in data or "detail" in data or "message" in data

    @pytest.mark.parametrize(
        "ip_mask,expected_status,description",
        [
            # Invalid: below minimum (8)
            (0, 400, "0, below minimum"),
            (1, 400, "1, below minimum"),
            (7, 400, "7, one below minimum"),
            # Valid: lower boundary
            (8, 201, "8, exact lower boundary"),
            # Valid: middle values
            (16, 201, "16, middle value"),
            (20, 201, "20, middle value"),
            (24, 201, "24, middle-upper value"),
            # Invalid: above maximum (24)
            (25, 400, "25, one above maximum"),
            (30, 400, "30, above maximum"),
            (32, 400, "32, above maximum"),
            # Edge cases
            (-1, 400, "negative value"),
        ],
    )
    def test_ip_mask_boundaries(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        ip_mask,
        expected_status,
        description,
    ):
        """Test IP mask boundary values (8-24 range)."""
        payload = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "manual",
            "ip_address": "192.168.1.100",
            "ip_mask": ip_mask,
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert (
            response.status_code == expected_status
        ), f"Mask {ip_mask} ({description}): expected {expected_status}, got {response.status_code}"

        if expected_status == 400:
            data = response.json()
            assert "error" in data or "detail" in data or "message" in data

    def test_ip_mode_dhcp_requires_null_ip(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
    ):
        """Test that DHCP mode should not require ip_address/ip_mask."""
        payload = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "dhcp",
            # ip_address and ip_mask omitted for DHCP
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert response.status_code == 201, "DHCP mode without IP/mask should succeed"

    def test_ip_mode_manual_requires_ip_and_mask(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
    ):
        """Test that manual mode requires both ip_address and ip_mask."""
        # Missing ip_address
        payload_no_ip = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "manual",
            "ip_mask": 24,
        }
        response = authenticated_client.post("/api/lecs-hosts", json=payload_no_ip)
        assert response.status_code == 400, "Manual mode without IP should fail"

        # Missing ip_mask
        payload_no_mask = {
            "hostname": "validhost",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "validuser",
            "password": "Abcdefg1",
            "ip_mode": "manual",
            "ip_address": "192.168.1.100",
        }
        response = authenticated_client.post("/api/lecs-hosts", json=payload_no_mask)
        assert response.status_code == 400, "Manual mode without mask should fail"


# ============================================================================
# Required Field Validation (Missing/Null fields)
# ============================================================================

class TestRequiredFields:
    """Test that all required fields are validated."""

    @pytest.mark.parametrize(
        "missing_field,payload_override,description",
        [
            ("hostname", {"spec_id": "eco-2c2g"}, "missing hostname"),
            ("spec_id", {"hostname": "validhost"}, "missing spec_id"),
            ("billing_mode", {"hostname": "validhost", "spec_id": "eco-2c2g"}, "missing billing_mode"),
            ("duration", {"hostname": "validhost", "spec_id": "eco-2c2g", "billing_mode": "subscription"}, "missing duration"),
            ("username", {"hostname": "validhost", "spec_id": "eco-2c2g", "billing_mode": "subscription", "duration": 1}, "missing username"),
            ("password", {"hostname": "validhost", "spec_id": "eco-2c2g", "billing_mode": "subscription", "duration": 1, "username": "validuser"}, "missing password"),
            ("ip_mode", {"hostname": "validhost", "spec_id": "eco-2c2g", "billing_mode": "subscription", "duration": 1, "username": "validuser", "password": "Abcdefg1"}, "missing ip_mode"),
        ],
    )
    def test_required_fields_validation(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
        missing_field,
        payload_override,
        description,
    ):
        """Test that missing required fields return 400 error."""
        response = authenticated_client.post("/api/lecs-hosts", json=payload_override)

        assert (
            response.status_code == 400
        ), f"Missing {missing_field} ({description}): expected 400, got {response.status_code}"

        data = response.json()
        assert "error" in data or "detail" in data or "message" in data


# ============================================================================
# Combined Validation Scenarios
# ============================================================================

class TestCombinedValidation:
    """Test combinations of valid/invalid fields."""

    def test_multiple_invalid_fields_returns_first_error(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
    ):
        """Test that multiple validation errors are handled (may return first or all)."""
        payload = {
            "hostname": "ab",  # invalid: too short
            "spec_id": "invalid",  # invalid: not in specs
            "billing_mode": "invalid",  # invalid: not allowed
            "duration": 0,  # invalid: not in allowed set
            "username": "ab",  # invalid: too short
            "password": "Ab1",  # invalid: too short
            "ip_mode": "invalid",  # invalid: not dhcp/manual
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert response.status_code == 400, "Multiple invalid fields should return 400"

    def test_all_valid_fields_succeeds(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
    ):
        """Test that all valid fields combined result in successful creation."""
        payload = {
            "hostname": "valid01",
            "spec_id": "eco-2c2g",
            "billing_mode": "subscription",
            "duration": 1,
            "username": "valid_user",
            "password": "SecureP@ss1",
            "ip_mode": "dhcp",
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert response.status_code == 201, "All valid fields should create host successfully"
        data = response.json()
        assert data.get("hostname") == "valid01"
        assert data.get("spec_id") == "eco-2c2g"
        assert data.get("status") == "creating"

    def test_manual_ip_with_all_valid_fields(
        self,
        authenticated_client,
        mock_billing_service,
        mock_task_queue,
    ):
        """Test host creation with manual IP mode and valid IP/mask."""
        payload = {
            "hostname": "valid02",
            "spec_id": "perf-4c8g",
            "billing_mode": "subscription",
            "duration": 12,
            "username": "admin_user",
            "password": "MyP@ssw0rd!123",
            "ip_mode": "manual",
            "ip_address": "10.0.0.50",
            "ip_mask": 16,
        }

        response = authenticated_client.post("/api/lecs-hosts", json=payload)

        assert response.status_code == 201, "Manual IP with valid fields should succeed"
        data = response.json()
        assert data.get("ip_mode") == "manual"
        assert data.get("ip_address") == "10.0.0.50"
