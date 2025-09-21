# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

# JWT configuration
SECRET_KEY = "supersecretvalueReynolds2450$"  # TODO: move to env for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # int minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any]) -> str:
    """
    Creates a short-lived access token with `exp` and `jti`.
    Expects `data` to already include {"sub": "<username>"}.
    """
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # <-- fix
    jti = str(uuid4())

    # python-jose accepts a datetime for "exp"
    to_encode.update({
        "exp": expire,
        "jti": jti,
        "type": "access",
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
