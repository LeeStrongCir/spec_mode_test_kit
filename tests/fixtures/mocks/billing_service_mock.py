"""Billing service mock for LECS host management integration tests.

Simulates the external billing/pricing system that calculates instance costs
and provides available instance specifications. This mock replaces real
network calls to the billing API during testing.

The mock maintains the same interface expected by the application service
layer, returning deterministic pricing data based on spec_id and billing mode.
"""

from typing import Optional


# Instance specs with pricing — mirrors data-model.md InstanceSpec table
INSTANCE_SPECS = [
    {"spec_id": "eco-2c2g", "instance_type": "economy", "name": "通用计算机", "vcpu": 2, "ram_gb": 2, "disk_gb": 40, "monthly_price": 100},
    {"spec_id": "eco-2c4g", "instance_type": "economy", "name": "通用计算机", "vcpu": 2, "ram_gb": 4, "disk_gb": 40, "monthly_price": 140},
    {"spec_id": "eco-2c8g", "instance_type": "economy", "name": "通用计算机", "vcpu": 2, "ram_gb": 8, "disk_gb": 40, "monthly_price": 180},
    {"spec_id": "eco-4c8g", "instance_type": "economy", "name": "通用计算机", "vcpu": 4, "ram_gb": 8, "disk_gb": 40, "monthly_price": 240},
    {"spec_id": "perf-2c4g", "instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 4, "disk_gb": 40, "monthly_price": 160},
    {"spec_id": "perf-2c8g", "instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 8, "disk_gb": 40, "monthly_price": 200},
    {"spec_id": "perf-4c8g", "instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 4, "ram_gb": 8, "disk_gb": 40, "monthly_price": 260},
    {"spec_id": "perf-8c16g", "instance_type": "high_performance", "name": "通用增强计算机", "vcpu": 8, "ram_gb": 16, "disk_gb": 40, "monthly_price": 500},
]

# Build lookup for fast spec retrieval
_SPEC_LOOKUP = {spec["spec_id"]: spec for spec in INSTANCE_SPECS}


class BillingServiceMock:
    """Mock billing service that returns deterministic pricing data.

    Implements the same interface as the real billing service:
    - calculate_cost: computes total cost given spec, billing mode, and duration
    - get_instance_specs: returns available instance specifications

    This mock does NOT make network calls — all data is computed locally
    from the INSTANCE_SPECS constant.
    """

    def __init__(self):
        """Initialize the billing service mock."""
        self._call_count = 0
        self._last_call = None
        self._error_mode = False
        self._custom_pricing = {}

    def set_error_mode(self, enabled: bool = True):
        """Toggle error mode to simulate billing service failures.

        Args:
            enabled: If True, subsequent calls will raise exceptions
        """
        self._error_mode = enabled

    def set_custom_price(self, spec_id: str, monthly_price: float):
        """Override the monthly price for a specific spec (for edge case testing).

        Args:
            spec_id: The spec to override (e.g., 'eco-2c2g')
            monthly_price: Custom monthly price in CNY
        """
        if spec_id in _SPEC_LOOKUP:
            self._custom_pricing[spec_id] = monthly_price
        else:
            raise ValueError(f"Unknown spec_id: {spec_id}")

    def reset_custom_pricing(self):
        """Remove all custom pricing overrides."""
        self._custom_pricing.clear()

    def calculate_cost(
        self,
        spec_id: str,
        billing_mode: str = "subscription",
        duration: int = 1,
    ) -> dict:
        """Calculate cost for an instance spec.

        Args:
            spec_id: Instance spec identifier (e.g., 'eco-2c2g')
            billing_mode: 'subscription' (包年包月) or 'on_demand' (按需计费)
            duration: Subscription duration in months (1–9, 12, 24)

        Returns:
            dict with keys:
                - unit_price: Monthly price (CNY)
                - duration: Duration in months
                - billing_mode: The billing mode used
                - total: Total cost (unit_price * duration for subscription)
                - currency: Always 'CNY'

        Raises:
            ValueError: If spec_id is not recognized
            RuntimeError: If error mode is enabled
        """
        self._call_count += 1
        self._last_call = {
            "spec_id": spec_id,
            "billing_mode": billing_mode,
            "duration": duration,
        }

        if self._error_mode:
            raise RuntimeError("Billing service unavailable")

        if spec_id not in _SPEC_LOOKUP and spec_id not in self._custom_pricing:
            raise ValueError(f"Unknown instance spec: {spec_id}")

        if spec_id in self._custom_pricing:
            unit_price = self._custom_pricing[spec_id]
        else:
            unit_price = _SPEC_LOOKUP[spec_id]["monthly_price"]

        if billing_mode == "subscription":
            total = unit_price * duration
        elif billing_mode == "on_demand":
            # On-demand: price per hour * estimated hours in duration months
            # Simplified: use same monthly rate but duration=1
            total = unit_price
            duration = 1
        else:
            raise ValueError(f"Unknown billing mode: {billing_mode}")

        return {
            "unit_price": unit_price,
            "duration": duration,
            "billing_mode": billing_mode,
            "total": total,
            "currency": "CNY",
        }

    def get_instance_specs(self) -> list[dict]:
        """Get list of all available instance specifications.

        Returns:
            list of dicts, each with keys:
                spec_id, instance_type, name, vcpu, ram_gb, disk_gb, monthly_price
        """
        self._call_count += 1
        self._last_call = {"method": "get_instance_specs"}

        if self._error_mode:
            raise RuntimeError("Billing service unavailable")

        specs = list(INSTANCE_SPECS)
        # Apply any custom pricing overrides
        for spec in specs:
            if spec["spec_id"] in self._custom_pricing:
                spec = dict(spec)  # Copy to avoid mutating original
                spec["monthly_price"] = self._custom_pricing[spec["spec_id"]]
        return specs

    def get_spec(self, spec_id: str) -> Optional[dict]:
        """Get a single instance spec by ID.

        Args:
            spec_id: Instance spec identifier

        Returns:
            dict with spec details, or None if not found
        """
        self._call_count += 1
        return _SPEC_LOOKUP.get(spec_id)

    @property
    def call_count(self) -> int:
        """Number of times any billing method was called."""
        return self._call_count

    @property
    def last_call(self) -> Optional[dict]:
        """Arguments of the last billing method call."""
        return self._last_call

    def reset(self):
        """Reset call tracking and custom pricing."""
        self._call_count = 0
        self._last_call = None
        self._error_mode = False
        self._custom_pricing.clear()
