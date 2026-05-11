import pytest


@pytest.mark.integration
class TestLecsHostAPI:
    async def test_get_hosts_empty(self):
        pass

    async def test_delete_host_not_found(self):
        pass

    async def test_get_instance_types(self):
        pass

    async def test_get_os_images(self):
        pass

    async def test_create_host_validation(self):
        pass

    async def test_create_host_quota_exceeded(self):
        pass
