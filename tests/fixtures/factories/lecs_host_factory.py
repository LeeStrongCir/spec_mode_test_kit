"""LECS Host factory for creating test host data in various lifecycle states.

Provides factory presets for normal, stopped, failed, creating, deleting,
and other host states. Each preset configures the appropriate fields
for that state, including status timestamps and billing information.
"""

import factory
import uuid
from datetime import datetime, timezone


# Instance spec constants from data model
INSTANCE_SPECS = {
    "eco-2c2g": {"instance_type": "economy", "vcpu": 2, "ram_gb": 2, "disk_gb": 40, "monthly_price": 100},
    "eco-2c4g": {"instance_type": "economy", "vcpu": 2, "ram_gb": 4, "disk_gb": 40, "monthly_price": 140},
    "eco-2c8g": {"instance_type": "economy", "vcpu": 2, "ram_gb": 8, "disk_gb": 40, "monthly_price": 180},
    "eco-4c8g": {"instance_type": "economy", "vcpu": 4, "ram_gb": 8, "disk_gb": 40, "monthly_price": 240},
    "perf-2c4g": {"instance_type": "high_performance", "vcpu": 2, "ram_gb": 4, "disk_gb": 40, "monthly_price": 160},
    "perf-2c8g": {"instance_type": "high_performance", "vcpu": 2, "ram_gb": 8, "disk_gb": 40, "monthly_price": 200},
    "perf-4c8g": {"instance_type": "high_performance", "vcpu": 4, "ram_gb": 8, "disk_gb": 40, "monthly_price": 260},
    "perf-8c16g": {"instance_type": "high_performance", "vcpu": 8, "ram_gb": 16, "disk_gb": 40, "monthly_price": 500},
}


class LECSHostFactory(factory.Factory):
    """Factory for creating LECS host test data dictionaries.

    Produces host data that matches the LECSHost SQLAlchemy model schema.
    Default configuration creates a normal, subscription-billed host
    with the eco-2c2g spec (economy, 2 vCPU, 2GB RAM).

    Attributes:
        id: UUID string, auto-generated
        user_id: UUID string of the host owner
        hostname: Machine-generated hostname
        billing_mode: 'subscription' or 'on_demand'
        instance_type: 'economy' or 'high_performance'
        spec_id: Instance spec identifier
        vcpu, ram_gb, system_disk_gb: Resource specs from spec_id
        os_image: Operating system image
        ip_mode: 'dhcp' or 'manual'
        status: Host lifecycle status
        duration: Subscription duration in months
        unit_price: Monthly price in CNY
        cost_info: Billing cost snapshot (JSON)
        username: Host access username (default 'root')
        password_hash: Hashed host password
        created_at, updated_at: Timestamps
    """

    class Meta:
        model = dict

    # Core identifiers
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    user_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    hostname = factory.LazyFunction(lambda: f"host-{uuid.uuid4().hex[:8]}")

    # Billing & spec (defaults to eco-2c2g subscription)
    billing_mode = "subscription"
    spec_id = "eco-2c2g"
    instance_type = factory.LazyAttribute(lambda o: INSTANCE_SPECS[o.spec_id]["instance_type"])
    vcpu = factory.LazyAttribute(lambda o: INSTANCE_SPECS[o.spec_id]["vcpu"])
    ram_gb = factory.LazyAttribute(lambda o: INSTANCE_SPECS[o.spec_id]["ram_gb"])
    system_disk_gb = factory.LazyAttribute(lambda o: INSTANCE_SPECS[o.spec_id]["disk_gb"])
    duration = 6
    unit_price = factory.LazyAttribute(lambda o: INSTANCE_SPECS[o.spec_id]["monthly_price"])
    cost_info = factory.LazyAttribute(
        lambda o: {
            "billing_mode": o.billing_mode,
            "unit_price": o.unit_price,
            "duration": o.duration,
            "total": o.unit_price * o.duration,
            "currency": "CNY",
        }
    )

    # Network & OS
    os_image = "huawei_euler"
    ip_mode = "dhcp"
    ip_address = None
    ip_mask = None

    # Status & lifecycle (default: normal)
    status = "normal"
    error_msg = None

    # Access credentials
    username = "root"
    password_hash = "$argon2id$v=19$m=65536,t=3,p=4$dummy$hostPassHash"

    # Soft delete
    deleted_at = None

    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """State presets for common host lifecycle scenarios."""

        # Ready-to-use host
        status_normal = factory.Trait(status="normal")

        # Host being provisioned (transient state)
        status_creating = factory.Trait(status="creating")

        # Host encountered error during provisioning
        status_failed = factory.Trait(
            status="failed",
            error_msg="Provisioning failed: resource unavailable",
        )

        # Host cleanly shut down
        status_stopped = factory.Trait(status="stopped")

        # Host in process of shutting down (transient)
        status_shutting_down = factory.Trait(status="shutting_down")

        # Host in process of starting (transient)
        status_starting = factory.Trait(status="starting")

        # Host being removed (transient)
        status_deleting = factory.Trait(status="deleting")

        # Soft-deleted host
        status_deleted = factory.Trait(
            status="deleted",
            deleted_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
        )

        # On-demand billing instead of subscription
        billing_on_demand = factory.Trait(
            billing_mode="on_demand",
            duration=1,
            cost_info=None,
        )

        # High performance spec preset
        spec_high_perf = factory.Trait(
            spec_id="perf-4c8g",
        )

        # Manual IP configuration
        ip_manual = factory.Trait(
            ip_mode="manual",
            ip_address="10.0.1.100",
            ip_mask=24,
        )

    @classmethod
    def create_normal(cls, user_id=None, **overrides):
        """Create a host in normal (running) state."""
        params = {"status": "normal"}
        if user_id:
            params["user_id"] = user_id
        params.update(overrides)
        return cls(**params)

    @classmethod
    def create_stopped(cls, user_id=None, **overrides):
        """Create a host in stopped state (ready for delete or start)."""
        params = {"status": "stopped"}
        if user_id:
            params["user_id"] = user_id
        params.update(overrides)
        return cls(**params)

    @classmethod
    def create_failed(cls, user_id=None, **overrides):
        """Create a host in failed state (ready for delete or retry start)."""
        params = {
            "status": "failed",
            "error_msg": "Provisioning failed: resource unavailable",
        }
        if user_id:
            params["user_id"] = user_id
        params.update(overrides)
        return cls(**params)

    @classmethod
    def create_creating(cls, user_id=None, **overrides):
        """Create a host in creating state (provisioning in progress)."""
        params = {"status": "creating"}
        if user_id:
            params["user_id"] = user_id
        params.update(overrides)
        return cls(**params)

    @classmethod
    def create_deleting(cls, user_id=None, **overrides):
        """Create a host in deleting state (removal in progress)."""
        params = {"status": "deleting"}
        if user_id:
            params["user_id"] = user_id
        params.update(overrides)
        return cls(**params)

    @classmethod
    def create_deleted(cls, user_id=None, **overrides):
        """Create a soft-deleted host."""
        params = {
            "status": "deleted",
            "deleted_at": datetime.now(timezone.utc),
        }
        if user_id:
            params["user_id"] = user_id
        params.update(overrides)
        return cls(**params)


def build_host_data(status="normal", user_id=None, spec_id=None, **overrides):
    """Convenience function to build a single host data dict.

    Useful for tests that need raw data without factory instance overhead.

    Args:
        status: Host status (normal, stopped, failed, creating, deleting, deleted)
        user_id: Owner user UUID string
        spec_id: Instance spec ID (e.g., 'eco-2c2g', 'perf-4c8g')
        **overrides: Additional field overrides

    Returns:
        dict matching LECSHost schema
    """
    params = {"status": status}
    if user_id:
        params["user_id"] = user_id
    if spec_id:
        params["spec_id"] = spec_id
    params.update(overrides)
    return LECSHostFactory(**params)


def build_hosts_data(count, status="normal", user_id=None, **overrides):
    """Build multiple host data dicts with the same configuration.

    Args:
        count: Number of hosts to create
        status: Shared status for all hosts
        user_id: Shared owner (can be overridden per-host)
        **overrides: Additional field overrides (can include 'user_ids' list)

    Returns:
        list of dicts matching LECSHost schema
    """
    user_ids = overrides.pop("user_ids", None)
    hosts = []
    for i in range(count):
        host_overrides = overrides.copy()
        if user_ids and i < len(user_ids):
            host_overrides["user_id"] = user_ids[i]
        elif user_id:
            host_overrides["user_id"] = user_id
        hosts.append(build_host_data(status=status, **host_overrides))
    return hosts
