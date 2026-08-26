import pytest

@pytest.mark.asyncio
async def test_not_exists(client):
    response = await client.get('/bad_request')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_login(client, user):
    response = await client.post('/login',
                           data={'username': user['email'],
                                 'password': user['password']})
    assert response.status_code == 200