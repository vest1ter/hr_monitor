from datetime import datetime, timedelta
from backend.utils import JWT
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from backend.services.auth_service import create_access_token, create_refresh_token, generate_tokens
from fastapi.routing import APIRouter
from backend.utils.JWT import verify_token, authenticate_user, get_current_user_role
from backend.schemas.auth_schemas import oauth2_scheme, LoginResponse, RefreshResponse, UserMeResponse, Tokens
from backend.databases_function.database_function import get_user_id
from jose import jwt


auth_router = APIRouter()


@auth_router.post("/auth/login", response_model=LoginResponse)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    tokens = Tokens(generate_tokens(user.username, user.role))
    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="Strict",  
        secure=False  
    )
    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {refresh_token}",
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  
        samesite="Lax",
        secure=False
    )
    return LoginResponse(
        access_token= access_token,
        token_type= "bearer",
        refresh_token= refresh_token
    )


@auth_router.post("/auth/refresh", response_model=RefreshResponse)
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")
    try:
        username = verify_token(refresh_token)
        role = get_current_user_role(refresh_token)
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token2")
    
    tokens = Tokens(generate_tokens(username, role))
    new_access_token = tokens.access_token
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="Lax",
        secure=False
    )
    return RefreshResponse(access_token = new_access_token, token_type= "bearer")


@auth_router.get("/auth/users/me", response_model=UserMeResponse)
async def read_users_me(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token found")
    return UserMeResponse(access_token = token)
