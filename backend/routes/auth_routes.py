from datetime import datetime, timedelta
from backend.utils import JWT
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from backend.services.auth_service import create_access_token, create_refresh_token
from fastapi.routing import APIRouter
from backend.utils.JWT import verify_token, authenticate_user
from backend.schemas.auth_schemas import oauth2_scheme
from backend.databases_function.database_function import get_user_id


auth_router = APIRouter()




@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"uuid": str(get_user_id(user.username)), "sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data = {"sub": user.username, "role": user.role}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
            }



@auth_router.get("/users/me")
async def read_users_me(token: str):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return {"token": verify_token(token)}