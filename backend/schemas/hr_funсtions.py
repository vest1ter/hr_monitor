from pydantic import BaseModel, UUID4, Field
from typing import Optional


class AddingResumeRequest(BaseModel):
    candidate_name: str
    position: str
    skills: Optional[str] = None
    work_experiens: Optional[int] = None
    salary_pred: Optional[int] = None
    source: Optional[str] = None

class MoveResume(BaseModel):
    candidate_name: str
    new_stage_name: str