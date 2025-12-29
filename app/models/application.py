from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class ApplicationBase(BaseModel):
    applicant_name: str
    applicant_email: EmailStr
    job_id: str
    match_score: int 
    ai_feedback: str 

class ApplicationDB(ApplicationBase):
    id: str = Field(..., alias="_id")
    applied_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True