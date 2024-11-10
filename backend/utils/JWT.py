import jwt
import datetime
from fastapi import HTTPException, status
from typing import Optional
from backend.config import SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES


