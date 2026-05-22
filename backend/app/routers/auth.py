from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Import Database và Models của ông
from app.database import get_db
from app.models.models import User

# Cấu hình bảo mật
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "KHTN_CA_SECRET_KEY_SIEUBAMAT" # Sau này deploy thực tế thì đưa cái này vào file .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Token sống trong 1 tiếng

security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==========================================
# PYDANTIC SCHEMAS (Định nghĩa Dữ liệu vào/ra)
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
# HÀM HỖ TRỢ (Tái sử dụng nhiều lần)
# ==========================================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Hàm này dùng để chặn các API yêu cầu đăng nhập. Sẽ bóc Token từ Header ra để kiểm tra."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn hoặc sai chữ ký")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    return user

# ==========================================
# API ENDPOINTS
# ==========================================

@router.post("/register")
async def register(user_data: UserAuth, db: Session = Depends(get_db)):
    """API Đăng ký tài khoản mới"""
    # 1. Kiểm tra username đã tồn tại chưa
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username này đã có người sử dụng")
    
    # 2. Băm mật khẩu (Hash)
    hashed_password = pwd_context.hash(user_data.password)
    
    # 3. Lưu vào Database
    new_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role="customer" # Mặc định đăng ký là customer
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Đăng ký tài khoản thành công!", "user_id": new_user.id}

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserAuth, db: Session = Depends(get_db)):
    """API Đăng nhập và trả về JWT Token"""
    # 1. Tìm user
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Sai username hoặc mật khẩu")
    
    # 2. Kiểm tra mật khẩu
    if not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Sai username hoặc mật khẩu")
    
    # 3. Tạo JWT Token
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
    current_user: User = Depends(get_current_user), # Ép phải có Token mới cho đổi
    db: Session = Depends(get_db)
):
    """API Đổi mật khẩu (Yêu cầu đăng nhập)"""
    # 1. Check mật khẩu cũ
    if not pwd_context.verify(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác")
    
    # 2. Hash mật khẩu mới và lưu
    current_user.password_hash = pwd_context.hash(data.new_password)
    db.commit()
    
    return {"message": "Đổi mật khẩu thành công!"}

@router.post("/register-admin-secret", tags=["Secret"])
async def register_admin_secret(user_data: UserAuth, db: Session = Depends(get_db)):
    """API ẩn dùng để khởi tạo tài khoản Admin hệ thống (Sau này deploy thực tế sẽ xóa đi)"""
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username này đã có người sử dụng")
    
    hashed_password = pwd_context.hash(user_data.password)
    
    # Điểm khác biệt duy nhất: Gắn mác quyền lực tối cao
    new_admin = User(
        username=user_data.username,
        password_hash=hashed_password,
        role="admin" 
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return {"message": "Đã tạo tài khoản Admin tối cao thành công!", "admin_id": new_admin.id}