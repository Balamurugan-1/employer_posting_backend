from fastapi import APIRouter, HTTPException, status, Request
from app.models.job import JobCreate, JobDB
from typing import List,Optional
from bson import ObjectId
from app.models.job import JobUpdate 
from app.services.gemini_service import analyze_jobs_with_gemini
from app.models.smart_search import SmartSearchRequest
from fastapi import Depends, Header
from typing import Annotated
from jose import jwt, JWTError
from app.core.config import settings
from datetime import datetime
from app.services.gemini_service import generate_job_description
from app.models.job import JDGenRequest

router = APIRouter()

#helper function
async def get_current_user(authorization: Annotated[str, Header()] = None):
    if not authorization:
         raise HTTPException(status_code=401, detail="Missing Authentication Token")

    try:
       
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
@router.post("/", response_description="Add new job", status_code=status.HTTP_201_CREATED, response_model=JobDB)
async def create_job(
    request: Request, 
    job: JobCreate, 
    current_user: str = Depends(get_current_user)
):
  
    job_data = job.model_dump()
    
    job_data["employer_email"] = current_user
    

    job_data["owner_email"] = current_user
    
  
    job_data["created_at"] = datetime.utcnow()

  
    new_job = await request.app.mongodb["jobs"].insert_one(job_data)

    created_job = await request.app.mongodb["jobs"].find_one({"_id": new_job.inserted_id})
    created_job["_id"] = str(created_job["_id"])
    
    return created_job


@router.get("/", response_description="List all jobs", response_model=List[JobDB])
async def list_jobs(
    request: Request, 
    limit: int = 100, 
    search: Optional[str] = None 
):
    query = {}
    
    if search:
        query = {"$text": {"$search": search}}
    
    jobs = []
    if search:
        cursor = request.app.mongodb["jobs"].find(query).limit(limit)
    else:
        cursor = request.app.mongodb["jobs"].find(query).sort("created_at", -1).limit(limit)
    
    async for document in cursor:
        document["_id"] = str(document["_id"])
        jobs.append(document)
        
    return jobs

@router.get("/my-jobs", response_description="List current user jobs", response_model=List[JobDB])
async def list_my_jobs(
    request: Request, 
    current_user: str = Depends(get_current_user)
):
    jobs = []

    cursor = request.app.mongodb["jobs"].find({"owner_email": current_user})
    
    async for document in cursor:
        document["_id"] = str(document["_id"])
        jobs.append(document)
        
    return jobs

#get
@router.get("/{id}", response_description="Get a single job", response_model=JobDB)
async def show_job(id: str, request: Request):
    if (job := await request.app.mongodb["jobs"].find_one({"_id": ObjectId(id)})) is not None:
        job["_id"] = str(job["_id"])
        return job

    raise HTTPException(status_code=404, detail=f"Job {id} not found")


#update
@router.put("/{id}", response_description="Update a job", response_model=JobDB)
async def update_job(id: str, request: Request, job: JobUpdate):
    job_data = {k: v for k, v in job.model_dump().items() if v is not None}

    if len(job_data) >= 1:
        update_result = await request.app.mongodb["jobs"].update_one(
            {"_id": ObjectId(id)}, {"$set": job_data}
        )

        if update_result.modified_count == 1:
            if (updated_job := await request.app.mongodb["jobs"].find_one({"_id": ObjectId(id)})) is not None:
                updated_job["_id"] = str(updated_job["_id"])
                return updated_job

    if (existing_job := await request.app.mongodb["jobs"].find_one({"_id": ObjectId(id)})) is not None:
        existing_job["_id"] = str(existing_job["_id"])
        return existing_job

    raise HTTPException(status_code=404, detail=f"Job {id} not found")

#delete
@router.delete("/{id}", response_description="Delete a job")
async def delete_job(id: str, request: Request):
    delete_result = await request.app.mongodb["jobs"].delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return {"message": "Job deleted successfully"}

    raise HTTPException(status_code=404, detail=f"Job {id} not found")

#smartsearch
@router.post("/smart-match")
async def smart_job_match(request: Request, search_data: SmartSearchRequest):
    jobs_cursor = request.app.mongodb["jobs"].find().sort("created_at", -1).limit(20)
    jobs_list = []
    
    async for doc in jobs_cursor:
        
        job_summary = {
            "id": str(doc["_id"]),
            "title": doc["title"],
            "company": doc["company_name"],
            "skills": doc.get("requirements", []),
            "description": doc["description"][:200] + "..." 
        }
        jobs_list.append(job_summary)

    ai_feedback = await analyze_jobs_with_gemini(search_data.query, jobs_list)
    
    return {"ai_response": ai_feedback}


@router.post("/generate-desc")
async def generate_desc_api(payload: JDGenRequest, current_user: str = Depends(get_current_user)):
    desc = await generate_job_description(payload.title, payload.company_name, payload.location)
    return {"description": desc}