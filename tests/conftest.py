from typing import Any, AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
