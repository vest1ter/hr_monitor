from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

class User(BaseModel):
    username: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
