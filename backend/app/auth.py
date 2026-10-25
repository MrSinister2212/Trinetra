import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_api_key() -> str:
    return "tri_" + secrets.token_hex(20)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    token_auth: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or missing API key",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Try API Key Header
    if api_key:
        query = select(User).where(User.api_key == api_key, User.is_active == True)
        result = await db.execute(query)
        user = result.scalars().first()
        if user:
            return user

    # 2. Try Bearer JWT
    if token_auth and token_auth.credentials:
        token = token_auth.credentials
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        query = select(User).where(User.username == username, User.is_active == True)
        result = await db.execute(query)
        user = result.scalars().first()
        if user is None:
            raise credentials_exception
        return user

    raise credentials_exception

async def ensure_default_analyst(db: AsyncSession):
    query = select(User).where(User.username == "analyst")
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        default_user = User(
            username="analyst",
            hashed_password=get_password_hash("trinetra2026"),
            api_key=generate_api_key(),
            role="admin",
            is_active=True
        )
        db.add(default_user)
        await db.commit()
        return default_user
    return user
