# app/core/dependencies.py (or wherever this lives)

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.base import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.models.user import RevokedToken  # <-- FIXED import

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def is_revoked(db: Session, jti: Optional[str]) -> bool:
    if not jti:
        return True
    # Optional: lightweight cleanup of expired rows
    db.query(RevokedToken).filter(
        RevokedToken.expires_at < datetime.now(tz=timezone.utc)
    ).delete(synchronize_session=False)
    db.commit()

    return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
) -> User:
    try:
        payload = decode_access_token(token)
        username: Optional[str] = payload.get("sub")
        jti: Optional[str] = payload.get("jti")
        ttype: Optional[str] = payload.get("type")
        if username is None or jti is None or ttype != "access":
            raise credentials_exception
        if is_revoked(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return user
