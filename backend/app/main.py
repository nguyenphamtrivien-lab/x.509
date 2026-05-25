"""
File: backend/app/main.py
Description: FastAPI main application entry point.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import models
from app.routers import auth, admin, customer

# Tạo DB tables (SQLite sẽ tự động tạo file .db)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="X.509 Certificate Management System API")

# Cấu hình CORS để frontend React gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Fix #7: Chỉ cho phép frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(customer.router)

@app.get("/")
async def root():
    return {"message": "Welcome to X.509 Certificate Management System API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
