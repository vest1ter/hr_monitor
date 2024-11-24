import uuid
from ..database import Base
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from fastapi import Depends, HTTPException, status
from backend.models.models import UserRole, User, Vacancy, Resume, Stage, ResumeStageHistory
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.schemas.teamlead_function import HRdata_request
from backend.utils.hashing import get_password_hash
from datetime import datetime, timedelta, timezone


def add_hr_user(data: HRdata_request):
    db: Session = get_db()
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )

    new_user = User(
        id=uuid4(),
        username=data.username,
        hashed_password=get_password_hash(data.password),
        role=UserRole.hr 
    )

    db.add(new_user)
    db.commit()

    return {"message": "HR user added successfully", "user_id": new_user.id}

def add_new_resume(resume: Resume):
    db: Session = get_db()
    
    try:
        print(resume.current_stage)
        db.add(resume)
        history_entry = ResumeStageHistory(
            id=uuid4(),
            resume_id=resume.id,
            stage_id=resume.current_stage,
            entered_at=datetime.now(timezone.utc),
            processed_by=resume.uploaded_by
        )
        db.add(history_entry)
        db.commit()
        db.refresh(resume)
    except:
        raise HTTPException(status_code=400, detail= "резюме не может быть добавлено")
    



def get_user_id(username: str):
    db: Session = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user.id

def get_vacancy_by_name(vacancy_name: str):
    db: Session = get_db()
    vacancy = db.query(Vacancy).filter(Vacancy.title == vacancy_name).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найденa")
    return vacancy

def get_stage_id(stage_name: str):
    db: Session = get_db()
    stage = db.query(Stage).filter(Stage.name == stage_name).first()
    if not stage:
        raise HTTPException(status_code=404, detail="стадии не сущесвует")
    return stage.id