from fastapi import Depends, HTTPException
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from fastapi.routing import APIRouter
from backend.schemas.hr_funсtions import AddingResumeRequest, MoveResume
from backend.models.models import Resume, ResumeStageHistory
from backend.utils.JWT import team_lead_required
from backend.databases_function.database_function import add_hr_user, get_vacancy_by_name, add_new_resume, get_stage_id, get_resume_by_name, move_resume_stage_in_db
from datetime import datetime, timedelta, timezone
from backend.utils.JWT import get_user_JWT_id
from uuid import uuid4

hr_control = APIRouter()

@hr_control.post("/add_resume")
async def add_resume(data: AddingResumeRequest, user_jwt: str, vacancy_name: str):
    vacancy_id = get_vacancy_by_name(vacancy_name).id
    current_user = get_user_JWT_id(user_jwt)
    current_stage = get_stage_id('open')

    new_resume = Resume(
        id = uuid4(),
        candidate_name=data.candidate_name,
        position=data.position,
        skills=data.skills,
        work_experiens=data.work_experiens,
        salary_pred=data.salary_pred,
        source=data.source,
        uploaded_at=datetime.now(timezone.utc),
        vacancy_id=vacancy_id,
        current_stage=current_stage,
        uploaded_by=current_user
    )

    add_new_resume(new_resume)
    
    return {"massage": 'sucsess', "resume": new_resume.id}
    

@hr_control.post("/move_resumes")
def move_resume_stage(data: MoveResume, user_jwt: str):
    current_user = get_user_JWT_id(user_jwt)

    resume = move_resume_stage_in_db(data, current_user)

    return {"message": "Резюме успешно перемещено", "resume": resume}