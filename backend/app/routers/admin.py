from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime

from app.database import get_db
from app.models.models import User, CertRequest, Certificate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

# ==========================================
# CHỐT KIỂM TRA QUYỀN ADMIN
# ==========================================
def get_admin_user(current_user: User = Depends(get_current_user)):
    """Hàm này kiểm tra xem user đang đăng nhập có phải là admin không"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Truy cập bị từ chối. Khu vực này chỉ dành cho Admin!"
        )
    return current_user

# ==========================================
# API ENDPOINTS
# ==========================================

@router.get("/requests/pending")
async def get_pending_requests(
    admin: User = Depends(get_admin_user), # Bắt buộc phải là Admin mới gọi được
    db: Session = Depends(get_db)
):
    """Lấy danh sách toàn bộ các yêu cầu cấp chứng chỉ (CSR) đang chờ duyệt"""
    requests = db.query(CertRequest).filter(CertRequest.status == "Pending").all()
    if not requests:
        return {"message": "Hiện tại không có yêu cầu nào đang chờ duyệt."}
    return requests

@router.post("/requests/{req_id}/approve")
async def approve_request(
    req_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Duyệt yêu cầu CSR và tiến hành cấp chứng chỉ"""
    
    # 1. Tìm cái đơn yêu cầu trong DB
    req = db.query(CertRequest).filter(CertRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu này")
    if req.status != "Pending":
        raise HTTPException(status_code=400, detail="Yêu cầu này đã được xử lý rồi")

    # 2. Đổi trạng thái đơn thành "Đã duyệt"
    req.status = "Approved"

    # 3. TẠO CHỨNG CHỈ (Chỗ này sau này sẽ cắm code Core Mật mã của M1 vào)
    # Tạm thời chúng ta sẽ tạo một chứng chỉ giả lập để test luồng DB
    new_cert = Certificate(
        user_id=req.user_id,
        serial_number=f"SN-{req.id}-{int(datetime.datetime.now().timestamp())}",
        subject="Đang chờ M1 bóc tách từ CSR", 
        issuer="KHTN CA",
        valid_from=datetime.datetime.utcnow(),
        valid_to=datetime.datetime.utcnow() + datetime.timedelta(days=365),
        status="Active",
        pem_data="-----BEGIN CERTIFICATE-----\n(BẠN M1 SẼ ĐỔ CHỮ KÝ VÀO ĐÂY)\n-----END CERTIFICATE-----"
    )
    
    db.add(new_cert)
    db.commit()

    return {
        "message": f"Duyệt thành công yêu cầu #{req_id}!", 
        "cert_serial": new_cert.serial_number
    }