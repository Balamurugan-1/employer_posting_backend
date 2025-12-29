from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserDB(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    hashed_password: str