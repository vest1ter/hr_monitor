from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Any, List
from datetime import datetime
from uuid import UUID


class HRdataRequest(BaseModel):
    username: str
    password: str


class VacancyCreateRequest(BaseModel):
    title: str
    description: Optional[str]
    required_skills: Optional[str]
    salary_range: Optional[str]


class ResumeOut(BaseModel):
    id: UUID
    skills: str
    salary_pred: int
    uploaded_at: datetime
    current_stage: UUID
    candidate_name: str
    position: str
    work_experiens: int
    source: str
    vacancy_id: UUID
    uploaded_by: UUID

    class Config:
        from_attributes = True


class ResumeFilterRequest(BaseModel):
    stage: Optional[str] = Field(None, description="Фильтр по стадии")
    position: Optional[str] = Field(None, description="Фильтр по вакансии")
    date_from: Optional[datetime] = Field(None, description="Фильтр: от даты")
    date_to: Optional[datetime] = Field(None, description="Фильтр: до даты")
    sort_by: Optional[str] = Field(
        "created_at", description="Сортировка: created_at или sla"
    )
    order: Optional[str] = Field("asc", description="Порядок: asc или desc")


class AddHRResponse(BaseModel):
    message: str
    data: HRdataRequest


class AddVacancyResponse(BaseModel):
    message: str
