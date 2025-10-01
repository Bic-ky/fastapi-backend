# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# ---- Load config from pydantic settings (cached) ----
_settings = get_settings()
SECRET_KEY: str = _settings.secret_key
ALGORITHM: str = _settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = getattr(_settings, "access_token_expire_minutes", 30)

# Fail fast if required settings are missing
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in settings/.env")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM is not set in settings/.env (e.g., HS256)")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# (Optional alias; keep if other code imports it)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any]) -> str:
    """
    Creates a short-lived access token with `exp` and `jti`.
    Expects `data` to already include {"sub": "<username>"}.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "jti": str(uuid4()),
        "type": "access",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    # `algorithms` must be a list
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
