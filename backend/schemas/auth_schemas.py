from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from typing import Optional


class User(BaseModel):
    username: str
    password: str
    role: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str]

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str

class UserMeResponse(BaseModel):
    access_token: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
