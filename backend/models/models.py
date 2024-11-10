import uuid
from ..database import Base
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum



class UserRole(str, enum.Enum):
    hr = "hr"
    team_lead = "team_lead"

class ResumeStage(str, enum.Enum):
    open = "открыта"
    reviewed = "изучена"
    interview = "интервью"
    interviewed = "прошли интервью"
    technical_interview = "техническое собеседование"
    tech_interview_passed = "пройдено техническое собеседование"
    offer = "оффер"


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    resume_uploaded = relationship("Resume", back_populates="uploaded_by_user")
    vacancy = relationship("Vacancy", back_populates="created_by_user")


class Vacancy(Base):
    __tablename__ = "vacancy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    required_skills = Column(Text, nullable=True)
    salary_range = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_by_user = relationship("User", back_populates="vacancy")

    resumes = relationship("Resume", back_populates="vacancy")


class Resume(Base):
    __tablename__ = "resume"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    skills = Column(Text, nullable=True)
    work_experiens = Column(Integer, nullable=True)
    salary_pred = Column(Integer, nullable=True)
    source = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    vacancy_id = Column(UUID(as_uuid=True), ForeignKey("vacancy.id"), nullable=False)
    vacancy = relationship("Vacancy", back_populates="resumes")

    current_stage = Column(UUID(as_uuid=True), ForeignKey("stage.id"), nullable=False)
    stage = relationship("Stage", back_populates="resumes")

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    uploaded_by_user = relationship("User", back_populates="resume_uploaded")

    history = relationship("ResumeStageHistory", back_populates="resume")


class Stage(Base):
    __tablename__ = "stage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(ResumeStage), nullable=False)
    sla = Column(Integer, nullable=False)

    resumes = relationship("Resume", back_populates="stage")
    history = relationship("ResumeStageHistory", back_populates="stage")


class ResumeStageHistory(Base):
    __tablename__ = "resume_stage_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)

    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume.id"), nullable=False)
    resume = relationship("Resume", back_populates="history")

    stage_id = Column(UUID(as_uuid=True), ForeignKey("stage.id"), nullable=False)
    stage = relationship("Stage", back_populates="history")

    processed_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    processed_by_user = relationship("User")


