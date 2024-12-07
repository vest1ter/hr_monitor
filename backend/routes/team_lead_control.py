from fastapi import Depends
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from fastapi.routing import APIRouter
from backend.schemas.teamlead_function import HRdata_request, VacancyCreate
from backend.utils.JWT import team_lead_required, get_user_JWT_id
from backend.databases_function.database_function import add_hr_user, add_new_vacancy
from uuid import uuid4
from backend.models.models import Vacancy
from datetime import datetime, timedelta, timezone



team_lead_control_router = APIRouter()





@team_lead_control_router.post("/add_hr")
async def add_hr(data: HRdata_request, role: str = Depends(team_lead_required)):
    add_hr_user(data)
    return {"message": "HR user added successfully"}


@team_lead_control_router.post("/add_vacancy")
def create_vacancy(vacancy_data: VacancyCreate, user_jwt: str, role: str = Depends(team_lead_required)):
    current_user = get_user_JWT_id(user_jwt)
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

    return {"message": "Вакансия успешно создана", "vacancy": new_vacancy}