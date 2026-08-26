from src.main import app
from src.crud import db_delete_user
from httpx import AsyncClient, ASGITransport
import pytest_asyncio

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8080") as client:
        yield client

@pytest_asyncio.fixture
async def user(client: AsyncClient):
    response = await client.post('/create_user', json={'name': 'test', 'email': 'my@test.com', 'password': 'testpassword'})

    assert response.status_code == 200

    data = response.json()
    user_id = data['id']
    yield {'email': data['email'], 'password': 'testpassword'}
    await db_delete_user(user_id)