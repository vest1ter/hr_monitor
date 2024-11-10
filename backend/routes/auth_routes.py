from datetime import datetime, timedelta
from backend.utils import JWT
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from backend.services.auth_service import authenticate_user, create_access_token, create_refresh_token, verify_token
from fastapi.routing import APIRouter
from backend.schemas.auth_schemas import oauth2_scheme


auth_router = APIRouter()




@auth_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Received username: {form_data.username}, password: {form_data.password}")
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    print(f"User {form_data.username} authenticated successfully")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print("------------------------------")
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    print(f"Access token created: {access_token[:20]}...")
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    print(f"Refresh token created: {refresh_token[:20]}...") 
    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
            }



@auth_router.get("/users/me")
async def read_users_me(token: str):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    return {"token": verify_token(token)}