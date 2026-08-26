from src.security import create_access_token, decode_access_token, SECRET
from datetime import datetime, timedelta, timezone
import jwt

def test_valid_token():
    token = create_access_token(72)
    decoded = decode_access_token(token)
    assert decoded == 72

def test_invalid_token():
    decoded = decode_access_token('this is bad token')
    assert decoded is None

def test_expired_token():
    expires = datetime.now(timezone.utc) - timedelta(minutes=5)
    payload = {
        'sub': '72',
        'exp': expires
    }
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    assert decode_access_token(token) is None