from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import datetime

from app.database import get_db
from app.models.models import Certificate

router = APIRouter(tags=["Public API"])

@router.get("/crl")
async def get_certificate_revocation_list(db: Session = Depends(get_db)):
    """
    Xuất Danh sách chứng chỉ bị thu hồi (CRL). 
    Đây là API Public, bất kỳ ai cũng có thể gọi để kiểm tra.
    """
    # Lục tìm toàn bộ chứng chỉ có trạng thái Revoked
    revoked_certs = db.query(Certificate).filter(Certificate.status == "Revoked").all()
    
    # Đóng gói thành định dạng danh sách đen
    revoked_list = []
    for cert in revoked_certs:
        revoked_list.append({
            "serial_number": cert.serial_number,
            "revocation_date": datetime.datetime.utcnow().isoformat() # Thực tế có thể lấy từ db nếu ông có cột thời gian thu hồi
        })
    
    # Trả về cấu trúc giả lập của một file CRL chuẩn X.509
    return {
        "issuer": "KHTN CA",
        "last_update": datetime.datetime.utcnow().isoformat(),
        "next_update": (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat(),
        "revoked_certificates": revoked_list
    }

@router.get("/ocsp/{serial_number}")
async def check_certificate_status(serial_number: str, db: Session = Depends(get_db)):
    """
    Giao thức OCSP (Online Certificate Status Protocol): 
    Kiểm tra trạng thái của một chứng chỉ cụ thể xem nó là Good, Revoked hay Unknown.
    """
    cert = db.query(Certificate).filter(Certificate.serial_number == serial_number).first()
    
    # Nếu không tìm thấy trong DB
    if not cert:
        return {
            "serial_number": serial_number,
            "status": "Unknown",
            "message": "Không tìm thấy chứng chỉ này trong hệ thống."
        }
    
    # Nếu tìm thấy, trả về trạng thái chuẩn OCSP
    ocsp_status = "Good" if cert.status == "Active" else "Revoked"
    
    return {
        "serial_number": serial_number,
        "status": ocsp_status,
        "check_time": datetime.datetime.utcnow().isoformat()
    }