import pytest


@pytest.mark.anyio
async def test_health_endpoint(async_client):
    response = await async_client.get('/api/v1/health/')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


@pytest.mark.anyio
async def test_root(async_client):
    response = await async_client.get('/')
    assert response.status_code == 200
    assert response.json()['message'] == 'Codex Health API'