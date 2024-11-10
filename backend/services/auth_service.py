from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.schemas.auth_schemas import User
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

#-------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    print(f"Creating access token with data: {data}, expires_delta: {expires_delta}")
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    print(f"Token will expire at: {expire}")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Encoded JWT: {encoded_jwt[:20]}...") 
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    print(f"Creating  token with data: {data}, expires_delta: {expires_delta}")
    to_encode = data.copy()
    expire = expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    print(f"Token will expire at: {expire}")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Encoded JWT: {encoded_jwt[:20]}...") 
    return encoded_jwt



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







fake_users_db = {
    "user1": {
        "username": "user1",
        "hashed_password": get_password_hash("password123"),
    }
}

def authenticate_user(username: str, password: str):
    print(f"Authenticating user: {username}")
    user = fake_users_db.get(username)
    if not user:
        print(f"User {username} not found")
        return False
    if not verify_password(password, user["hashed_password"]):
        print(f"Incorrect password for {username}")
        return False
    print(f"User {username} authenticated successfully")
    return User(username=username, password=password)
