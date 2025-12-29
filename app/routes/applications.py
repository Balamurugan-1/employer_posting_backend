
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Request
from app.models.application import ApplicationDB
from app.services.gemini_service import score_resume
from bson import ObjectId
from pypdf import PdfReader
from datetime import datetime
import io

router = APIRouter()

@router.post("/apply")
async def apply_for_job(
    request: Request,
    file: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(...),
    job_id: str = Form(...)
):
   
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    content = await file.read()
    pdf = PdfReader(io.BytesIO(content))
    resume_text = ""
    for page in pdf.pages:
        resume_text += page.extract_text()


    job = await request.app.mongodb["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")


    analysis = await score_resume(resume_text, job.get("description", ""))

  
    application_data = {
        "job_id": job_id,
        "applicant_name": name,
        "applicant_email": email,
        "resume_text": resume_text[:2000],
        "match_score": analysis.get("score", 0),
        "ai_feedback": analysis.get("feedback", ""),
        "applied_at": datetime.utcnow()
    }
    
    new_app = await request.app.mongodb["applications"].insert_one(application_data)
    
    return {"message": "Application submitted successfully!", "score": analysis.get("score")}

@router.get("/{job_id}")
async def get_applications(job_id: str, request: Request):
    apps = []
    cursor = request.app.mongodb["applications"].find({"job_id": job_id}).sort("match_score", -1)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        apps.append(doc)
    return apps