import uuid
from ..database import Base
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer, asc, desc
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
from typing import Optional, List



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
    

def add_new_vacancy(vacancy: Vacancy):
    db: Session = get_db()    
    try:
        db.add(vacancy)
        db.commit()
        db.refresh(vacancy)
    except:
        raise HTTPException(status_code=400, detail= "вакансия не может быть добавлено")
    

def get_resume_by_name(candidate_name, db):
    resume = db.query(Resume).filter(Resume.candidate_name == candidate_name).first()
    if not resume:
        raise HTTPException(status_code=404, detail="резюме не найдено")

    return resume


def get_stage_by_name(stage_name, db):
    stage = db.query(Stage).filter(Stage.id == stage_name).first()
    if not stage:
        raise HTTPException(status_code=404, detail="стадии не существует")

    return stage


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


def get_resumes(
    db: Session,
    stage: Optional[str] = None,
    position: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "asc",
) -> List[Resume]:
    query = db.query(Resume)

    # Фильтры
    if stage:
        query = query.join(Stage).filter(Stage.name == stage)
    if position:
        query = query.filter(Resume.position == position)
    if date_from:
        query = query.filter(Resume.uploaded_at >= date_from)
    if date_to:
        query = query.filter(Resume.uploaded_at <= date_to)

    # Сортировка
    if sort_by == "created_at":
        query = query.order_by(asc(Resume.uploaded_at) if order == "asc" else desc(Resume.uploaded_at))
    elif sort_by == "sla":
        query = query.join(Stage).order_by(asc(Stage.sla) if order == "asc" else desc(Stage.sla))

    return query.all()




def move_resume_stage_in_db(data, current_user):
    db: Session = get_db()
    resume = get_resume_by_name(data.candidate_name, db)
    new_stage = get_stage_id(data.new_stage_name)

    current_history = db.query(ResumeStageHistory).filter(
        ResumeStageHistory.resume_id == resume.id,
        ResumeStageHistory.stage_id == resume.current_stage,
        ResumeStageHistory.left_at.is_(None),  # Последняя активная стадия
    ).first()
    if current_history:
        current_history.left_at = datetime.now(timezone.utc)  # Завершение текущей стадии


    resume.current_stage = new_stage

    # Создание записи в истории переходов
    new_history = ResumeStageHistory(
        id=uuid4(),
        resume_id=resume.id,
        stage_id=new_stage,
        entered_at=datetime.now(timezone.utc),
        processed_by=current_user,  # ID текущего пользователя
    )

    db.add(new_history)
    db.commit()
    db.refresh(resume)

    return resume