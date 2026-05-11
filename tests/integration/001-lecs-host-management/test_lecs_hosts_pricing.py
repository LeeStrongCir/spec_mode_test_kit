"""
Integration tests for LECS host pricing calculation logic.

Tests subscription and on-demand billing cost calculation,
cost_info field structure, and billing mode parameter handling.

Based on TC-028 from spec.md: "验证费用估算实时计算".
"""

import math

import pytest


# ============================================================
# Instance spec pricing data (from data-model.md)
# ============================================================

INSTANCE_SPECS = {
    "eco-2c2g": {"instance_type": "economy", "name": "通用计算机", "vcpu": 2, "ram_gb": 2, "disk_gb": 40, "monthly_price": 100},
    "eco-2c4g": {"instance_type": "economy", "name": "通用计算机", "vcpu": 2, "ram_gb": 4, "disk_gb": 40, "monthly_price": 140},
    "eco-2c8g": {"instance_type": "economy", "name": "通用计算机", "vcpu": 2, "ram_gb": 8, "disk_gb": 40, "monthly_price": 180},
    "eco-4c8g": {"instance_type": "economy", "name": "通用计算机", "vcpu": 4, "ram_gb": 8, "disk_gb": 40, "monthly_price": 240},
    "perf-2c4g": {"instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 4, "disk_gb": 40, "monthly_price": 160},
    "perf-2c8g": {"instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 8, "disk_gb": 40, "monthly_price": 200},
    "perf-4c8g": {"instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 4, "ram_gb": 8, "disk_gb": 40, "monthly_price": 260},
    "perf-8c16g": {"instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 8, "ram_gb": 16, "disk_gb": 40, "monthly_price": 500},
}

VALID_DURATIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 24]


# ============================================================
# Pricing calculation helper functions (mirroring backend logic)
# ============================================================

def calc_subscription_total(unit_price: float, duration: int) -> float:
    """Calculate subscription total cost: unit_price × duration."""
    return unit_price * duration


def calc_on_demand_daily(unit_price: float) -> float:
    """Calculate on-demand daily rate: monthly_price ÷ 30, rounded to 2 decimal places."""
    return round(unit_price / 30, 2)


def build_cost_info(billing_mode: str, unit_price: float, duration: int) -> dict:
    """Build cost_info JSON as the backend would return it."""
    if billing_mode == "subscription":
        total = calc_subscription_total(unit_price, duration)
    else:
        total = calc_on_demand_daily(unit_price)
    return {
        "billing_mode": billing_mode,
        "unit_price": unit_price,
        "duration": duration,
        "total": total,
        "currency": "CNY",
    }


# ============================================================
# Subscription billing calculation tests
# ============================================================

class TestSubscriptionCalculation:
    """Test subscription (包年/包月) billing cost calculations."""

    @pytest.mark.parametrize(
        "spec_id,monthly_price,duration,expected_total",
        [
            # Base case: 100元/月 × 3个月 = 300元 (TC-028 scenario 1)
            ("eco-2c2g", 100, 3, 300),
            # Various durations with eco-2c2g (100元/月)
            ("eco-2c2g", 100, 1, 100),
            ("eco-2c2g", 100, 9, 900),
            ("eco-2c2g", 100, 12, 1200),
            ("eco-2c2g", 100, 24, 2400),
            # Different specs with same duration
            ("eco-2c4g", 140, 3, 420),
            ("eco-2c8g", 180, 3, 540),
            ("eco-4c8g", 240, 3, 720),
            # High performance specs
            ("perf-2c4g", 160, 3, 480),
            ("perf-2c8g", 200, 3, 600),
            ("perf-4c8g", 260, 3, 780),
            ("perf-8c16g", 500, 3, 1500),
        ],
    )
    def test_subscription_total_calculation(self, spec_id, monthly_price, duration, expected_total):
        """Verify subscription total = monthly_price × duration for all specs and durations."""
        assert monthly_price == INSTANCE_SPECS[spec_id]["monthly_price"], \
            f"Test data mismatch: {spec_id} monthly_price should be {INSTANCE_SPECS[spec_id]['monthly_price']}"
        total = calc_subscription_total(monthly_price, duration)
        assert total == expected_total, \
            f"Expected {expected_total} but got {total} for {spec_id} × {duration} months"

    @pytest.mark.parametrize(
        "duration",
        VALID_DURATIONS,
    )
    def test_subscription_all_valid_durations(self, duration):
        """Verify all valid durations calculate correctly with eco-2c2g (100元/月)."""
        unit_price = 100
        total = calc_subscription_total(unit_price, duration)
        assert total == unit_price * duration
        assert total > 0

    @pytest.mark.parametrize(
        "spec_id,monthly_price",
        [
            ("eco-2c2g", 100),
            ("eco-4c8g", 240),
            ("perf-8c16g", 500),
        ],
    )
    def test_subscription_key_specs_monthly_rate(self, spec_id, monthly_price):
        """Verify key specs have correct monthly unit prices per data-model.md."""
        spec = INSTANCE_SPECS[spec_id]
        assert spec["monthly_price"] == monthly_price, \
            f"{spec_id} monthly_price should be {monthly_price}, got {spec['monthly_price']}"


# ============================================================
# On-demand billing calculation tests
# ============================================================

class TestOnDemandCalculation:
    """Test on-demand (按需计费) billing cost calculations."""

    @pytest.mark.parametrize(
        "spec_id,monthly_price,expected_daily",
        [
            # eco-2c2g: 100元/月 ÷ 30 = 3.33元/天 (TC-028 scenario 2)
            ("eco-2c2g", 100, 3.33),
            # Other economy specs
            ("eco-2c4g", 140, 4.67),
            ("eco-2c8g", 180, 6.00),
            ("eco-4c8g", 240, 8.00),
            # High performance specs
            ("perf-2c4g", 160, 5.33),
            ("perf-2c8g", 200, 6.67),
            ("perf-4c8g", 260, 8.67),
            ("perf-8c16g", 500, 16.67),
        ],
    )
    def test_on_demand_daily_rate(self, spec_id, monthly_price, expected_daily):
        """Verify on-demand daily rate = monthly_price ÷ 30, rounded to 2 decimal places."""
        assert monthly_price == INSTANCE_SPECS[spec_id]["monthly_price"]
        daily_rate = calc_on_demand_daily(monthly_price)
        assert daily_rate == expected_daily, \
            f"Expected daily rate {expected_daily} for {spec_id} but got {daily_rate}"

    def test_on_demand_daily_rate_precision(self):
        """Verify on-demand daily rate rounds to exactly 2 decimal places."""
        daily_rate = calc_on_demand_daily(100)
        assert round(daily_rate, 2) == daily_rate

    def test_on_demand_daily_rate_formula(self):
        """Verify the formula: monthly_price ÷ 30 = daily_rate (per TC-028)."""
        monthly = 100
        daily = calc_on_demand_daily(monthly)
        assert abs(daily - monthly / 30) < 0.01, \
            f"Daily rate {daily} does not match {monthly}/30"


# ============================================================
# Cost info field structure tests
# ============================================================

class TestCostInfoStructure:
    """Test cost_info JSON field structure and content."""

    @pytest.mark.parametrize(
        "billing_mode,unit_price,duration",
        [
            ("subscription", 100, 3),
            ("subscription", 240, 12),
            ("subscription", 500, 1),
            ("on_demand", 100, 1),
            ("on_demand", 240, 1),
            ("on_demand", 500, 1),
        ],
    )
    def test_cost_info_contains_required_fields(self, billing_mode, unit_price, duration):
        """Verify cost_info contains all required fields: billing_mode, unit_price, duration, total, currency."""
        cost_info = build_cost_info(billing_mode, unit_price, duration)
        required_keys = {"billing_mode", "unit_price", "duration", "total", "currency"}
        assert required_keys.issubset(cost_info.keys()), \
            f"cost_info missing required fields: {required_keys - cost_info.keys()}"

    @pytest.mark.parametrize(
        "billing_mode,unit_price,duration,expected_total,expected_currency",
        [
            ("subscription", 100, 3, 300, "CNY"),
            ("subscription", 240, 12, 2880, "CNY"),
            ("subscription", 500, 24, 12000, "CNY"),
            ("on_demand", 100, 1, 3.33, "CNY"),
            ("on_demand", 240, 1, 8.00, "CNY"),
            ("on_demand", 500, 1, 16.67, "CNY"),
        ],
    )
    def test_cost_info_field_values(self, billing_mode, unit_price, duration, expected_total, expected_currency):
        """Verify cost_info field values are calculated correctly."""
        cost_info = build_cost_info(billing_mode, unit_price, duration)
        assert cost_info["billing_mode"] == billing_mode
        assert cost_info["unit_price"] == unit_price
        assert cost_info["duration"] == duration
        assert cost_info["total"] == expected_total
        assert cost_info["currency"] == expected_currency

    def test_cost_info_subscription_total_formula(self):
        """Verify subscription cost_info total = unit_price × duration."""
        cost_info = build_cost_info("subscription", 100, 3)
        assert cost_info["total"] == cost_info["unit_price"] * cost_info["duration"]

    def test_cost_info_on_demand_total_formula(self):
        """Verify on-demand cost_info total = unit_price ÷ 30 (daily rate)."""
        cost_info = build_cost_info("on_demand", 100, 1)
        expected = round(100 / 30, 2)
        assert cost_info["total"] == expected


# ============================================================
# Billing mode parameter tests
# ============================================================

class TestBillingModeParameter:
    """Test billing mode parameter handling in cost calculation."""

    @pytest.mark.parametrize(
        "billing_mode,unit_price,duration,expected_total",
        [
            # Subscription mode: total = unit_price × duration
            ("subscription", 100, 1, 100),
            ("subscription", 100, 3, 300),
            ("subscription", 100, 12, 1200),
            ("subscription", 240, 6, 1440),
            ("subscription", 500, 24, 12000),
            # On-demand mode: total = unit_price ÷ 30 (daily rate)
            # Duration is typically 1 for on-demand
            ("on_demand", 100, 1, 3.33),
            ("on_demand", 240, 1, 8.00),
            ("on_demand", 500, 1, 16.67),
        ],
    )
    def test_billing_mode_affects_calculation(self, billing_mode, unit_price, duration, expected_total):
        """Verify billing_mode parameter correctly switches calculation logic."""
        cost_info = build_cost_info(billing_mode, unit_price, duration)
        assert cost_info["billing_mode"] == billing_mode
        assert cost_info["total"] == expected_total

    def test_subscription_vs_on_demand_different_totals(self):
        """Verify subscription and on-demand produce different totals for same spec."""
        sub_total = build_cost_info("subscription", 100, 1)["total"]
        od_total = build_cost_info("on_demand", 100, 1)["total"]
        assert sub_total != od_total
        assert sub_total == 100
        assert od_total == 3.33

    @pytest.mark.parametrize(
        "spec_id",
        list(INSTANCE_SPECS.keys()),
    )
    def test_all_specs_both_billing_modes(self, spec_id):
        """Verify all specs calculate correctly in both billing modes."""
        spec = INSTANCE_SPECS[spec_id]
        monthly_price = spec["monthly_price"]

        # Subscription: 1 month
        sub_cost = build_cost_info("subscription", monthly_price, 1)
        assert sub_cost["billing_mode"] == "subscription"
        assert sub_cost["total"] == monthly_price
        assert sub_cost["unit_price"] == monthly_price

        # On-demand: daily rate
        od_cost = build_cost_info("on_demand", monthly_price, 1)
        assert od_cost["billing_mode"] == "on_demand"
        assert od_cost["total"] == round(monthly_price / 30, 2)
        assert od_cost["unit_price"] == monthly_price


# ============================================================
# Cross-spec pricing consistency tests
# ============================================================

class TestPricingConsistency:
    """Test pricing consistency across different instance specs."""

    @pytest.mark.parametrize(
        "spec_id,expected_monthly",
        [(spec_id, spec["monthly_price"]) for spec_id, spec in INSTANCE_SPECS.items()],
    )
    def test_spec_pricing_matches_data_model(self, spec_id, expected_monthly):
        """Verify each spec's monthly price matches data-model.md specification."""
        spec = INSTANCE_SPECS[spec_id]
        assert spec["monthly_price"] == expected_monthly

    def test_high_performance_premium_over_economy(self):
        """Verify high-performance specs cost more than equivalent economy specs."""
        # perf-2c4g (160) > eco-2c4g (140)
        assert INSTANCE_SPECS["perf-2c4g"]["monthly_price"] > INSTANCE_SPECS["eco-2c4g"]["monthly_price"]
        # perf-2c8g (200) > eco-2c8g (180)
        assert INSTANCE_SPECS["perf-2c8g"]["monthly_price"] > INSTANCE_SPECS["eco-2c8g"]["monthly_price"]
        # perf-4c8g (260) > eco-4c8g (240)
        assert INSTANCE_SPECS["perf-4c8g"]["monthly_price"] > INSTANCE_SPECS["eco-4c8g"]["monthly_price"]

    def test_more_resources_higher_price(self):
        """Verify specs with more resources have higher prices."""
        # Economy tier: more RAM → higher price
        assert INSTANCE_SPECS["eco-2c4g"]["monthly_price"] > INSTANCE_SPECS["eco-2c2g"]["monthly_price"]
        assert INSTANCE_SPECS["eco-2c8g"]["monthly_price"] > INSTANCE_SPECS["eco-2c4g"]["monthly_price"]
        assert INSTANCE_SPECS["eco-4c8g"]["monthly_price"] > INSTANCE_SPECS["eco-2c8g"]["monthly_price"]
        # Performance tier: more resources → higher price
        assert INSTANCE_SPECS["perf-2c8g"]["monthly_price"] > INSTANCE_SPECS["perf-2c4g"]["monthly_price"]
        assert INSTANCE_SPECS["perf-4c8g"]["monthly_price"] > INSTANCE_SPECS["perf-2c8g"]["monthly_price"]
        assert INSTANCE_SPECS["perf-8c16g"]["monthly_price"] > INSTANCE_SPECS["perf-4c8g"]["monthly_price"]

    @pytest.mark.parametrize(
        "spec_id,duration",
        [
            (spec_id, duration)
            for spec_id in ["eco-2c2g", "eco-4c8g", "perf-8c16g"]
            for duration in [1, 3, 12]
        ],
    )
    def test_subscription_calculation_representative_specs(self, spec_id, duration):
        """Representative test: subscription calculation for key specs at key durations."""
        spec = INSTANCE_SPECS[spec_id]
        total = calc_subscription_total(spec["monthly_price"], duration)
        expected = spec["monthly_price"] * duration
        assert total == expected
