from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
import datetime
from typing import Optional
import config_back

app = FastAPI()


SECRET_KEY = config_back.SECRET_KEY
ALGORITHM = config_back.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config_back.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = config_back.REFRESH_TOKEN_EXPIRE_DAYS

# Инициализация схемы аутентификации для FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Создаём модель для пользователя
class User(BaseModel):
    username: str
    password: str

# Функция для создания Access Token
def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для создания Refresh Token
def create_refresh_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=expires_delta or REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Маршрут для логина, возвращающий Access и Refresh токены
@app.post("/token")
async def login(user: User):
    # Проверка данных пользователя (здесь используется простой пример без базы данных)
    if user.username == "admin" and user.password == "password":
        # Создание токенов
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Функция для проверки токена
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Маршрут для обновления Access Token с использованием Refresh Token
@app.post("/refresh")
async def refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    username = verify_token(refresh_token)
    new_access_token = create_access_token(data={"sub": username})
    return {"access_token": new_access_token, "token_type": "bearer"}

# Пример защищённого маршрута
@app.get("/protected-route")
async def protected_route(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    return {"message": f"Hello, {username}!"}
