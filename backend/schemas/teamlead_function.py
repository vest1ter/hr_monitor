from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer


class HRdata_request(BaseModel):
    username: str
    password: str

