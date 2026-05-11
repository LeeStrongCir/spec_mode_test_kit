"""User factory for creating test user data in LECS host management tests.

Uses Factory Boy patterns to create consistent, reusable user fixtures
with configurable roles (user/admin).
"""

import factory
from datetime import datetime, timezone


class UserFactory(factory.Factory):
    """Factory for creating test user dictionaries.

    This factory produces user data dictionaries that can be used
    to create User model instances in tests. It follows Factory Boy
    patterns with LazyFunction for dynamic values.

    Attributes:
        id: UUID string, auto-generated
        username: Unique username based on sequence
        email: Fake email address
        role: User role ('user' or 'admin')
        status: User status, defaults to 'active'
        created_at: Current UTC datetime
    """

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(factory.Faker("uuid4")))
    username = factory.Sequence(lambda n: f"testuser_{n:04d}")
    email = factory.Faker("email")
    role = "user"
    status = "active"
    password_hash = factory.LazyFunction(
        lambda: "$argon2id$v=19$m=65536,t=3,p=4$dummy$hash"
    )
    failed_login_count = 0
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """Role parameter presets for quick user type selection."""

        role_user = factory.Trait(role="user")
        role_admin = factory.Trait(role="admin", username="admin")

    @classmethod
    def create_user(cls, **overrides):
        """Create a standard user with 'user' role."""
        return cls(role="user", **overrides)

    @classmethod
    def create_admin(cls, **overrides):
        """Create an admin user with 'admin' role."""
        return cls(role="admin", username="admin", **overrides)
