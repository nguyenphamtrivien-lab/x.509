from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.database import get_db
from app.models.models import User

# Security Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "KHTN_CA_SECRET_KEY_SIEUBAMAT" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================
class UserAuth(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ==========================================
# DEPENDENCIES
# ==========================================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Extract and validate JWT token to authenticate users"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token has expired or signature is invalid.")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User account does not exist.")
    return user

# ==========================================
# API ENDPOINTS
# ==========================================

@router.post("/register")
async def register(user_data: UserAuth, db: Session = Depends(get_db)):
    """Register a new customer account"""
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already registered.")
    
    hashed_password = pwd_context.hash(user_data.password)
    
    new_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role="customer" 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User successfully registered.", "user_id": new_user.id}

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserAuth, db: Session = Depends(get_db)):
    """Authenticate user and return JWT Token"""
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    if not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.username,
        "id": user.id,
        "role": user.role,
        "exp": expire_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return TokenResponse(access_token=token, role=user.role)

@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    if not pwd_context.verify(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password.")
    
    current_user.password_hash = pwd_context.hash(data.new_password)
    db.commit()
    
    return {"message": "Password successfully updated."}

@router.post("/register-admin-secret", tags=["Secret"])
async def register_admin_secret(user_data: UserAuth, db: Session = Depends(get_db)):
    """Secret endpoint for initializing superadmin account (To be removed in production)"""
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already registered.")
    
    hashed_password = pwd_context.hash(user_data.password)
    
    new_admin = User(
        username=user_data.username,
        password_hash=hashed_password,
        role="admin" 
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return {"message": "Superadmin account successfully created.", "admin_id": new_admin.id}