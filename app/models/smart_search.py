from pydantic import BaseModel

class SmartSearchRequest(BaseModel):
    query: str