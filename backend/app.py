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
from backend.routes.team_lead_control import team_lead_control_router
from backend.routes.hr_control import hr_control

app = FastAPI()

app.include_router(team_lead_control_router)
app.include_router(auth_router)
app.include_router(hr_control)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:3000"] для ограниченных доменов
    allow_credentials=True,
    allow_methods=["*"],  # или более ограниченно, например, ["GET", "POST"]
    allow_headers=["*"],  # или ограничьте заголовки
)
