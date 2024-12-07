from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from typing import Optional


class HRdata_request(BaseModel):
    username: str
    password: str

class VacancyCreate(BaseModel):
    title: str
    description: Optional[str]
    required_skills: Optional[str]
    salary_range: Optional[str]

