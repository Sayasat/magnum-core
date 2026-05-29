from httpx import AsyncClient


async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "magnum-go",
    }