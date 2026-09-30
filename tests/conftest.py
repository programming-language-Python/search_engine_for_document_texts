import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture(scope="session")
async def test_client():
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
            yield client
