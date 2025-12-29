from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.routes.jobs import router as job_router
from app.routes.auth import router as auth_router

app = FastAPI(title="Job Portal API")


origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["Auth"], prefix="/auth")

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    
    try:
        await app.mongodb["jobs"].create_index([
            ("title", "text"),
            ("description", "text"),
            ("requirements", "text")
        ])
    except Exception:
        pass
    
    print("✅ Connected to MongoDB Atlas successfully!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    print("🛑 MongoDB connection closed.")

app.include_router(job_router, tags=["Jobs"], prefix="/jobs")

@app.get("/")
async def root():
    return {"message": "Job Portal API is running"}