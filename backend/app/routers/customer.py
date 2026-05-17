from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.models import User, CertRequest, Certificate
from app.routers.auth import get_current_user # Import chốt bảo vệ từ auth.py

router = APIRouter(prefix="/customer", tags=["Customer"])

# ==========================================
# PYDANTIC SCHEMAS (Chuẩn hóa dữ liệu)
# ==========================================
class CSRSubmitRequest(BaseModel):
    csr_data: str

class CertResponse(BaseModel):
    id: int
    serial_number: str
    subject: str
    issuer: str
    valid_from: str
    valid_to: str
    status: str

# ==========================================
# API ENDPOINTS
# ==========================================

@router.post("/submit-csr")
async def submit_csr(
    data: CSRSubmitRequest, 
    current_user: User = Depends(get_current_user), # Bắt buộc phải có JWT Token
    db: Session = Depends(get_db)
):
    """API nộp file yêu cầu chứng chỉ (CSR)"""
    
    # 1. Tạo một bản ghi mới trong bảng cert_requests
    new_request = CertRequest(
        user_id=current_user.id,
        csr_data=data.csr_data,
        status="Pending" # Vừa nộp thì trạng thái là Chờ duyệt
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return {
        "message": "Đã tiếp nhận yêu cầu CSR thành công!", 
        "request_id": new_request.id,
        "status": new_request.status
    }

@router.get("/certs")
async def list_certs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API lấy danh sách toàn bộ chứng chỉ của user đang đăng nhập"""
    
    certs = db.query(Certificate).filter(Certificate.user_id == current_user.id).all()
    if not certs:
        return {"message": "Bạn chưa có chứng chỉ nào."}
    
    return certs

@router.post("/certs/{cert_id}/request-revoke")
async def request_revoke(
    cert_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API gửi yêu cầu thu hồi chứng chỉ khi bị lộ Key"""
    
    # Tìm chứng chỉ xem có đúng là của user này không
    cert = db.query(Certificate).filter(
        Certificate.id == cert_id, 
        Certificate.user_id == current_user.id
    ).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Không tìm thấy chứng chỉ này")
    
    if cert.status == "Revoked":
        raise HTTPException(status_code=400, detail="Chứng chỉ này đã bị thu hồi từ trước rồi")
    
    # Cập nhật trạng thái thành chờ thu hồi (Chờ Admin duyệt)
    cert.status = "Revoke_Pending"
    db.commit()
    
    return {"message": "Đã gửi yêu cầu thu hồi thành công, chờ Admin phê duyệt."}