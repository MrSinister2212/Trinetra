from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User
from app.schemas import TokenResponse, UserResponse, UserCreate
from app.auth import verify_password, get_password_hash, create_access_token, generate_api_key, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == credentials.username)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(data={"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/regenerate-api-key", response_model=UserResponse)
async def regenerate_api_key_endpoint(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.api_key = generate_api_key()
    await db.commit()
    await db.refresh(current_user)
    return current_user
