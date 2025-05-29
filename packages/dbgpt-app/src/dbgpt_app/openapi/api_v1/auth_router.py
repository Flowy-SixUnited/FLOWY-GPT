from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from pydantic import BaseModel
from datetime import timedelta
from typing import Optional
import hashlib
import time

router = APIRouter()

# Mock settings - In production, these should be in a config file
JWT_SECRET_KEY = "a_very_secret_key_for_dbgpt"  # CHANGE THIS IN PRODUCTION
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()  # Simple hash for demo, use passlib in prod

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta.total_seconds()
    else:
        expire = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"exp": expire})
    # In a real app, use: encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    # For this mock, we'll just return a string indicating the user
    return f"mock-jwt-{to_encode.get('sub')}-{to_encode.get('user_id')}"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    nick_name: Optional[str] = None
    role: Optional[str] = None

# 模拟用户数据库 (实际应从数据库查询)
# Store hashed passwords!
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("password"), 
        "user_id": "001",
        "nick_name": "Admin User",
        "role": "admin",
        "disabled": False,
    },
    "user": {
        "username": "user",
        "hashed_password": get_password_hash("password"),
        "user_id": "002",
        "nick_name": "Normal User",
        "role": "normal",
        "disabled": False,
    }
}

async def get_user_from_db(username: str):
    if username in fake_users_db:
        return fake_users_db[username]
    return None

@router.post("/token", response_model=TokenResponse, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = await get_user_from_db(form_data.username)
    if not user_dict or user_dict["disabled"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_dict["username"], "user_id": user_dict["user_id"], "role": user_dict["role"]}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user_dict["user_id"],
        "username": user_dict["username"],
        "nick_name": user_dict["nick_name"],
        "role": user_dict["role"]
    }
