from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.core.auth import verify_password, get_password_hash, create_access_token, get_current_user
from app.core.config import settings
from app.models.db_models import UserModel

router = APIRouter()


class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Validate password length (bcrypt limit is 72 bytes)
    if len(user_data.password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too long. Maximum length is 72 characters."
        )
    
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )
    
    # Check if user already exists
    existing_user = db.query(UserModel).filter(
        (UserModel.email == user_data.email) | (UserModel.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user (truncate password to 72 bytes if needed as a safeguard)
    password_bytes = user_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password_to_hash = password_bytes.decode('utf-8', errors='ignore')
    else:
        password_to_hash = user_data.password
    
    hashed_password = get_password_hash(password_to_hash)
    db_user = UserModel(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(id=str(db_user.id), email=db_user.email, username=db_user.username)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    # OAuth2PasswordRequestForm uses 'username' field for both username and email
    user = db.query(UserModel).filter(
        (UserModel.username == form_data.username) | (UserModel.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(id=str(user.id), email=user.email, username=user.username)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(id=str(current_user.id), email=current_user.email, username=current_user.username)
