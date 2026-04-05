# UserCreate, UserLogin, UserOut
# UserCreate      → username, email, password, role
# UserLogin       → email, password
# UserOut         → id, username, email, role, created_at
# TokenOut        → access_token, token_type

from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime



class TokenOut(BaseModel):
    access_token: str
    token_type: str
