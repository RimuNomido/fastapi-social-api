import pytest

@pytest.mark.asyncio
async def test_not_exists(client):
    response = await client.get('/bad_request')
    assert response.status_code == 404

@pytest.mark.parametrize(
    'email, expected_status', [
        ('my@test.com', 409),
        ('unique@user.com', 200)
    ]
)

@pytest.mark.asyncio
async def test_create_user(client, email: str, expected_status: int, user, cleanup_user):
    response = await client.post('/create_user', json={'name': 'testing', 'email': email, 'password': 'unique_password'})
    if response.status_code == 200:
        user = response.json()
        cleanup_user.append(user['id'])
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_login(client, user):
    response = await client.post('/login',
                           data={'username': user['email'],
                                 'password': user['password']})
    assert response.status_code == 200

@pytest.mark.parametrize(
    'password, expected_status', [
        ('short', 422),
        ('ultrasupertoolongpasswordforregistration', 422),
        ('nicepassword', 200),
        ('goodpassword', 200),
    ]
)

@pytest.mark.asyncio
async def test_password_requirements(client, password:str, expected_status: int, cleanup_user):
    response = await client.post('/create_user', json={'name': 'password_test', 'email': 'valid@password.com', 'password': password})
    if response.status_code == 200:
        user = response.json()
        cleanup_user.append(user['id'])
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    'password, expected_status', [
        ('bambalam', 401),
        ('blackbetty', 401),
        ('supernoob228', 401),
        ('realpassword', 401),
        ('testpassword', 200),
    ]
)

@pytest.mark.asyncio
async def test_login_password(client, password: str, expected_status: int, cleanup_user, user):
    login_response = await client.post('/login', data={'username': user['email'], 'password': password})
    assert login_response.status_code == expected_status

@pytest.mark.asyncio
async def test_protected_posts(client, user, cleanup_posts):
    login_response = await client.post('/login', data={'username': user['email'], 'password': user['password']})
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    post_response = await client.post('/create_post', json={
        'title': 'testingTitle',
        'description': 'testingDescription',
        },
        headers=headers
    )
    assert post_response.status_code == 200

    post_data = post_response.json()
    cleanup_posts.append(post_data['id'])

    assert user['id'] == post_data['author_id']

@pytest.mark.asyncio
async def test_unauthorized_post(client, user, cleanup_posts):
    post_response = await client.post('/create_post', json={
        'title': 'testingTitle',
        'description': 'testingDescription',
    })
    assert post_response.status_code == 401

@pytest.mark.asyncio
async def test_protected_comments(client, user, cleanup_posts, cleanup_comments, post):
    post_data, token = post
    headers = {'Authorization': f'Bearer {token}'}
    comment_response = await client.post('/comments', json={
        'post_id': post_data['id'],
        'description': 'testingDescription',
    }, headers=headers)
    assert comment_response.status_code == 200
    comment_data = comment_response.json()
    cleanup_comments.append(comment_data['id'])
    assert user['id'] == comment_data['user_id']

@pytest.mark.asyncio
async def test_unauthorized_comment(client, user, cleanup_comments, post):
    post_data, _ = post
    comment_response = await client.post('/comments', json={
        'post_id': post_data['id'],
        'description': 'testingDescription',
    })
    assert comment_response.status_code == 401