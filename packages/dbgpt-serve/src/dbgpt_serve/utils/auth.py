import logging
from typing import Optional

from fastapi import Header, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer 

from dbgpt._private.pydantic import BaseModel

logger = logging.getLogger(__name__)

# oauth2_scheme should point to your token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token") 

class UserRequest(BaseModel):
    user_id: Optional[str] = None
    user_no: Optional[str] = None
    real_name: Optional[str] = None
    # same with user_id
    user_name: Optional[str] = None
    user_channel: Optional[str] = None
    role: Optional[str] = "normal"
    nick_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    nick_name_like: Optional[str] = None

# Mock settings (should be same as in auth_router.py or from a shared config)
JWT_SECRET_KEY_AUTH = "a_very_secret_key_for_dbgpt"
ALGORITHM_AUTH = "HS256"

def decode_access_token_mock(token: str):
    # Real decoding:
    # try:
    #     payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    #     username: Optional[str] = payload.get("sub")
    #     user_id: Optional[str] = payload.get("user_id")
    #     role: Optional[str] = payload.get("role")
    #     if username is None or user_id is None:
    #         return None
    #     return {"username": username, "user_id": user_id, "role": role}
    # except JWTError:
    #     return None

    # Mock decoding based on the mock token format: "mock-jwt-{username}-{user_id}"
    parts = token.split('-')
    if len(parts) == 4 and parts[0] == "mock" and parts[1] == "jwt":
        username = parts[2]
        user_id = parts[3]
        # Simulate role based on username for mock
        role = "admin" if username == "admin" else "normal"
        return {"username": username, "user_id": user_id, "role": role, "nick_name": username.capitalize()}
    return None

async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> UserRequest:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token_mock(token)  # Use real jwt.decode in production
    if payload is None:
        raise credentials_exception
    
    # You might want to fetch full user details from DB here if token only contains IDs/username
    # user_from_db = await user_service.get_user_by_id(payload.get("user_id"))
    # if user_from_db is None:
    #     raise credentials_exception

    return UserRequest(
        user_id=payload.get("user_id"), 
        user_no=payload.get("user_id"),  # same as user_id for compatibility
        user_name=payload.get("username"), 
        user_channel=payload.get("username"),  # fallback to username
        role=payload.get("role"), 
        nick_name=payload.get("nick_name", payload.get("username")),  # Fallback for nick_name
        real_name=payload.get("nick_name", payload.get("username"))  # Fallback for real_name
    )

def get_user_from_headers(user_id: Optional[str] = Header(None)):
    try:
        # Mock User Info - Keep for backward compatibility
        if user_id:
            return UserRequest(
                user_id=user_id, role="admin", nick_name=user_id, real_name=user_id
            )
        else:
            return UserRequest(
                user_id="001", role="admin", nick_name="dbgpt", real_name="dbgpt"
            )
    except Exception as e:
        logging.exception("Authentication failed!")
        raise Exception(f"Authentication failed. {str(e)}")
