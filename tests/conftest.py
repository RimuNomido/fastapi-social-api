from src.main import app
from src.crud import db_delete_user, db_delete_post, db_delete_comment
from httpx import AsyncClient, ASGITransport
import pytest_asyncio

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8080") as client:
        yield client

@pytest_asyncio.fixture
async def new_user(client: AsyncClient):
    response = await client.post('/create_user', json={'name': 'test','email': 'my@test.com', 'password': 'testpassword'})
    assert response.status_code == 200
    user = response.json()
    user_id = user['id']
    yield user
    await db_delete_user(user_id)

@pytest_asyncio.fixture
async def cleanup_user():
    ids_to_delete = []
    yield ids_to_delete
    for user_id in ids_to_delete:
        await db_delete_user(user_id)

@pytest_asyncio.fixture
async def cleanup_posts():
    ids_to_delete = []
    yield ids_to_delete
    for post_id in ids_to_delete:
        await db_delete_post(post_id)

@pytest_asyncio.fixture
async def user(client: AsyncClient, new_user: dict):
    user = new_user
    yield {'id': user['id'], 'email': user['email'], 'password': 'testpassword'}

@pytest_asyncio.fixture
async def cleanup_comments():
    ids_to_delete = []
    yield ids_to_delete
    for comment_id in ids_to_delete:
        await db_delete_comment(comment_id)

@pytest_asyncio.fixture
async def post(client: AsyncClient, user: dict, cleanup_posts):
    login_response = await client.post('/login', data={'username': user['email'], 'password': user['password']})
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    post_response = await client.post('/create_post', json={
        'title': 'testingTitle',
        'description': 'testingDescription',
    }, headers=headers
                                      )
    post_data = post_response.json()
    yield (post_data, token)
    cleanup_posts.append(post_data['id'])