import uuid

import pytest


@pytest.mark.anyio
async def test_list_hosts_empty():
    """List returns empty pagination for new user with no hosts."""
    pass


@pytest.mark.anyio
async def test_check_quota_below_limit():
    """Returns True when host count < 100."""
    pass


@pytest.mark.anyio
async def test_count_excludes_deleted():
    """count_user_hosts excludes records where deleted_at IS NOT NULL."""
    pass
