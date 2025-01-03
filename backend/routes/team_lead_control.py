from fastapi import Depends, HTTPException
from backend.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from fastapi.routing import APIRouter
from backend.schemas.teamlead_function import (
    HRdataRequest,
    VacancyCreateRequest,
    ResumeOut,
    ResumeFilterRequest,
    AddHRResponse,
    AddVacancyResponse,
)
from backend.utils.JWT import team_lead_required, get_user_JWT_id
from backend.databases_function.database_function import (
    add_hr_user,
    add_new_vacancy,
    get_resumes,
)
from uuid import uuid4
from backend.models.models import Vacancy, Resume
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session
from backend.database import get_db


team_lead_control_router = APIRouter()


@team_lead_control_router.post("/team_lead_control/add_hr", response_model=AddHRResponse)
async def add_hr(data: HRdataRequest, role: str = Depends(team_lead_required)):
    add_hr_user(data)
    return AddHRResponse(message="HR user added successfully", data=data)


@team_lead_control_router.post("/team_lead_control/add_vacancy")
def create_vacancy(
    vacancy_data: VacancyCreateRequest,
    user_jwt: str,
    role: str = Depends(team_lead_required),
):
    current_user = get_user_JWT_id(user_jwt)
    print("-------------------", current_user)
    new_vacancy = Vacancy(
        id=uuid4(),
        title=vacancy_data.title,
        description=vacancy_data.description,
        required_skills=vacancy_data.required_skills,
        salary_range=vacancy_data.salary_range,
        created_by=current_user,
        created_at=datetime.now(timezone.utc),
    )
    add_new_vacancy(new_vacancy)
    return AddVacancyResponse(
        message="Вакансия успешно создана",
    )


@team_lead_control_router.get("/team_lead_control/resumes", response_model=List[ResumeOut])
def list_resumes(
    filters: ResumeFilterRequest = Depends(),
    role: str = Depends(team_lead_required),
    db: Session = Depends(get_db),
):
    try:
        resumes = get_resumes(
            db=db,
            stage=filters.stage,
            position=filters.position,
            date_from=filters.date_from,
            date_to=filters.date_to,
            sort_by=filters.sort_by,
            order=filters.order,
        )
        #return List[ResumeOut]
        print(type(resumes), type(resumes[0]))
        return resumes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
