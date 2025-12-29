from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str = Field(..., min_length=3, example="Senior Backend Engineer")
    company_name: str = Field(..., min_length=1, example="Tech Corp")
    company_url: Optional[str] = Field(None, example="https://techcorp.com")
    location: str = Field(..., example="Remote")
    description: str = Field(..., min_length=10, description="Detailed job description")
    requirements: List[str] = Field(default=[], example=["Python", "FastAPI", "MongoDB"])
    salary_range: Optional[str] = Field(None, example="$100k - $140k")
    employer_email: EmailStr = Field(..., example="hr@techcorp.com") 

class JobCreate(JobBase):
    pass

class JobDB(JobBase):
    id: str = Field(..., alias="_id") 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_email: str = Field(...)

    class Config:
        populate_by_name = True

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_url: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    salary_range: Optional[str] = None
    employer_email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Backend Engineer (Updated)",
                "salary_range": "$120k - $150k"
            }
        }

class JDGenRequest(BaseModel):
    title: str
    company_name: str
    location: str