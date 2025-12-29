from fastapi import APIRouter, HTTPException, status, Request
from app.models.user import UserAuth
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from datetime import timedelta

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: Request, user: UserAuth):
    
    existing_user = await request.app.mongodb["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

  
    hashed_pass = get_password_hash(user.password)


    user_doc = {"email": user.email, "hashed_password": hashed_pass}
    await request.app.mongodb["users"].insert_one(user_doc)

    return {"message": "User created successfully"}

@router.post("/login")
async def login(request: Request, user: UserAuth):
    user_in_db = await request.app.mongodb["users"].find_one({"email": user.email})
    if not user_in_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user.password, user_in_db["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}