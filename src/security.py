from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import bcrypt
import jwt
import os

load_dotenv()
SECRET = os.getenv('SECRET')

def hash_password(raw_password: str) -> str:
    password_bytes = raw_password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    return hashed_password.decode('utf-8')

def verify_password(raw_password: str, hashed_password: str) -> bool:
    password_bytes = raw_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))

def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "exp": expires
    }

    token = jwt.encode(payload, SECRET, algorithm='HS256')

    return token

def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        return int(payload['sub'])
    except jwt.InvalidTokenError:
        return None