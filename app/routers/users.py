from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import or_
from app.models.user import RevokedToken
from app.core.dependencies import oauth2_scheme 
from app.core.dependencies import get_current_user, get_db_session
from app.core.security import decode_access_token, get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db_session)):
    db_user = db.query(User).filter(User.username == user.username or User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", tags=["authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    print(form_data.username , form_data.password)
    user = db.query(User).filter(
    or_(User.username == form_data.username, User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/logout", tags=["authentication"])
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    payload = decode_access_token(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    ttype = payload.get("type", "access")

    if not jti or not exp:
        raise HTTPException(status_code=400, detail="Invalid token payload")

    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)

    exists = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if not exists:
        db.add(RevokedToken(
            jti=jti,
            user_id=current_user.id,
            token_type=ttype,
            revoked_at=datetime.now(tz=timezone.utc),
            expires_at=expires_at,
        ))
        db.commit()

    return {"detail": "Logged out successfully"}

### Get Current User Endpoint (Protected) ###
@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user



### CRUD Endpoints (Protected) ###
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}