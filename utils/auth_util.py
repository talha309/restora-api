# restora-api/utils/auth_util.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
API_KEY_NAME = "x-api-key"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ──────────────────────────────────────
# Hash / Verify password
# ──────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ──────────────────────────────────────
# Create JWT access token
# ──────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        print("create_access_token error:", e)
        return None


# ──────────────────────────────────────
# Verify raw token (returns payload dict)
# ──────────────────────────────────────
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        if decoded:
            return decoded
        raise HTTPException(status_code=401, detail="Token not parseable")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print("verify_token error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")


# ──────────────────────────────────────
# Verify API key
# ──────────────────────────────────────
def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if api_key == os.getenv("API_KEY"):
        return api_key
    raise HTTPException(status_code=401, detail="Invalid API Key")


# ──────────────────────────────────────
# Get current user → returns real User object from DB
# ──────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decodes the JWT token and returns a lightweight user dict with
    'id' (int) and 'role' (str) pulled from the token payload.
    Routes access: current_user["id"], current_user["role"]
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        user_id = decoded.get("sub")
        role = decoded.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Return a simple namespace so routes can do current_user.id / current_user.role
        class _User:
            pass
        u = _User()
        u.id = int(user_id)
        u.role = role          # already a string ("admin", "waiter", etc.)
        return u

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        print("get_current_user error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")