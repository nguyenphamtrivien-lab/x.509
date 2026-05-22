from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# SỬA LỖI Ở ĐÂY: Thêm "app." vào trước đường dẫn
from app.database import engine
from app.models.models import Base

# Yêu cầu SQLAlchemy tự động dò class và tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(title="X.509 Certificate Management System")

# Cấu hình CORS cho Frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import auth
app.include_router(auth.router)
from app.routers import customer
app.include_router(customer.router)
from app.routers import admin 
app.include_router(admin.router) 
from app.routers import public  
app.include_router(public.router)  

@app.get("/")
async def root():
    return {
        "message": "Welcome to X.509 CA API",
        "status": "CORS and Database connection are ready!"
    }