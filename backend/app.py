from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import datetime
from typing import Optional
import backend.config
from backend.utils import JWT
from backend.schemas.user import User
from backend.routes.auth_routes import auth_router

app = FastAPI()

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:3000"] для ограниченных доменов
    allow_credentials=True,
    allow_methods=["*"],  # или более ограниченно, например, ["GET", "POST"]
    allow_headers=["*"],  # или ограничьте заголовки
)