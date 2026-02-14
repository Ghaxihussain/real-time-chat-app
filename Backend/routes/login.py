from ..config.database import get_db
from ..config.database import User
from fastapi import FastAPI, APIRouter, Depends, Response
from ..schemas.account_schemas import Signup, SignIn
from fastapi import Cookie, status, HTTPException
from fastapi.responses import JSONResponse
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from ..helpers.authentication_helpers import verify_password, get_password_hash, create_access_token, create_refresh_token
from sqlalchemy import select
from datetime import datetime
router = APIRouter(tags = ["Auhthentication"], prefix = "/auth")



@router.post("/signup")
async def signup(user: Signup, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    
    new_user = User(username=user.username, name=user.name, password=get_password_hash(user.password))
    db.add(new_user)
    await db.commit()
    return JSONResponse(content="User Created", status_code=status.HTTP_201_CREATED)



@router.post("/signin")
async def signin(user_input: SignIn, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_input.username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    if not verify_password(user_input.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    token = create_access_token({
        "username": user.username,
        "name": user.name
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  
    )
    return {"message": "Logged in"}
    

