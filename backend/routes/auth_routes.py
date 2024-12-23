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
from backend.services.auth_service import create_access_token, create_refresh_token
from fastapi.routing import APIRouter
from backend.utils.JWT import verify_token, authenticate_user, get_current_user_role
from backend.schemas.auth_schemas import oauth2_scheme, LoginResponse, RefreshResponse, UserMeResponse
from backend.databases_function.database_function import get_user_id
from jose import jwt


auth_router = APIRouter()


@auth_router.post("/login", response_model=LoginResponse)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "uuid": str(get_user_id(user.username)),
            "sub": user.username,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={
            "uuid": str(get_user_id(user.username)),
            "sub": user.username,
            "role": user.role,
        },
        expires_delta=refresh_token_expires,
    )
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


@auth_router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: Request, response: Response):
    '''
    # Генерируем новый access токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "role": role},
        expires_delta=access_token_expires,
    )
    '''
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
    # Проверка refresh токена (ваша логика)
    new_access_token = create_access_token(data={
            "uuid": str(get_user_id(username)),
            "sub": username,
            "role": role,
        })
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="Lax",
        secure=False
    )
    return RefreshResponse(access_token = new_access_token, token_type= "bearer")


@auth_router.get("/users/me", response_model=UserMeResponse)
async def read_users_me(request: Request):
    '''
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing"
        )
    return {"token": verify_token(token)}
    '''
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token found")
    return UserMeResponse(access_token = token)
