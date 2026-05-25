"""
File: backend/app/routers/admin.py
Description: Administrator endpoints for managing the CA and certificates.
Fix #2: Thêm endpoint quản lý yêu cầu thu hồi
Fix #13: Thêm db.rollback() khi exception
Fix #11: Thay utcnow() bằng datetime.now(timezone.utc)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from app.database import get_db
from app.models.models import User, CertRequest, Certificate, SystemConfig, AuditLog
from app.dependencies import get_current_admin
from app.services.crypto.cert_issue import generate_root_ca, sign_csr
from app.services.crypto.crl_manager import generate_crl

router = APIRouter(prefix="/admin", tags=["Admin"])

class RootCaRequest(BaseModel):
    password: str

class ConfigUpdate(BaseModel):
    key: str
    value: str

@router.get("/config")
async def get_config(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Lấy danh sách cấu hình hệ thống."""
    return db.query(SystemConfig).all()

@router.get("/csrs")
async def list_csrs(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Lấy danh sách các yêu cầu cấp chứng chỉ."""
    return db.query(CertRequest).order_by(CertRequest.created_at.desc()).all()

@router.get("/all-certs")
async def list_all_certs(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Lấy danh sách tất cả chứng chỉ đã cấp."""
    return db.query(Certificate).all()

# Fix #2: Endpoint quản lý yêu cầu thu hồi
@router.get("/revoke-requests")
async def list_revoke_requests(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Lấy danh sách yêu cầu thu hồi chứng chỉ đang chờ duyệt."""
    return db.query(Certificate).filter(Certificate.status == "revoke_pending").all()

@router.put("/config")
async def update_config(req: ConfigUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Cập nhật hoặc thêm cấu hình mới."""
    config = db.query(SystemConfig).filter(SystemConfig.config_key == req.key).first()
    if config:
        config.config_value = req.value
    else:
        db.add(SystemConfig(config_key=req.key, config_value=req.value))
    db.commit()
    return {"message": "Config updated"}

@router.post("/gen-root-ca")
async def gen_root_ca(req: RootCaRequest, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Generate a new Root CA và lưu vào SystemConfig."""
    try:
        root_key, root_cert = generate_root_ca(password=req.password)
        
        for key, value in [("root_key_pem", root_key), ("root_cert_pem", root_cert)]:
            config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            if config:
                config.config_value = value
            else:
                db.add(SystemConfig(config_key=key, config_value=value))
        
        db.add(AuditLog(user_id=current_admin.id, action="GEN_ROOT_CA", timestamp=datetime.now(timezone.utc)))
        db.commit()
        return {"message": "Root CA generated and saved successfully"}
    except Exception as e:
        db.rollback()  # Fix #13
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approve-csr/{csr_id}")
async def approve_csr(csr_id: int, req: RootCaRequest, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Approve a CSR and issue certificate."""
    csr_req = db.query(CertRequest).filter(CertRequest.id == csr_id, CertRequest.status == "pending").first()
    if not csr_req:
        raise HTTPException(status_code=404, detail="Pending CSR not found")

    root_key_cfg = db.query(SystemConfig).filter(SystemConfig.config_key == "root_key_pem").first()
    root_cert_cfg = db.query(SystemConfig).filter(SystemConfig.config_key == "root_cert_pem").first()
    if not root_key_cfg or not root_cert_cfg:
        raise HTTPException(status_code=500, detail="Root CA not found in system")

    try:
        cert_pem = sign_csr(
            csr_pem_str=csr_req.csr_data,
            root_key_pem_str=root_key_cfg.config_value,
            root_cert_pem_str=root_cert_cfg.config_value,
            root_password=req.password,
            valid_days=365
        )
        from cryptography import x509
        cert_obj = x509.load_pem_x509_certificate(cert_pem.encode('utf-8'))
        serial_hex = format(cert_obj.serial_number, 'x')

        new_cert = Certificate(
            user_id=csr_req.user_id,
            serial_number=serial_hex,
            subject=str(cert_obj.subject),
            issuer=str(cert_obj.issuer),
            valid_from=cert_obj.not_valid_before_utc,
            valid_to=cert_obj.not_valid_after_utc,
            status="active",
            pem_data=cert_pem
        )
        db.add(new_cert)
        csr_req.status = "approved"
        db.add(AuditLog(user_id=current_admin.id, action="APPROVE_CSR", timestamp=datetime.now(timezone.utc), details=f"Approved CSR {csr_id}"))
        db.commit()
        return {"message": "Certificate issued successfully"}
    except Exception as e:
        db.rollback()  # Fix #13
        raise HTTPException(status_code=400, detail=f"Failed to sign CSR: {str(e)}")

@router.post("/reject-csr/{csr_id}")
async def reject_csr(csr_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Từ chối yêu cầu CSR."""
    csr_req = db.query(CertRequest).filter(CertRequest.id == csr_id, CertRequest.status == "pending").first()
    if not csr_req:
        raise HTTPException(status_code=404, detail="Pending CSR not found")
    
    csr_req.status = "rejected"
    db.add(AuditLog(user_id=current_admin.id, action="REJECT_CSR", timestamp=datetime.now(timezone.utc), details=f"Rejected CSR {csr_id}"))
    db.commit()
    return {"message": "CSR rejected"}

@router.post("/revoke-cert/{cert_id}")
async def revoke_cert(cert_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Revoke an issued certificate."""
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if cert.status == "revoked":
        raise HTTPException(status_code=400, detail="Certificate already revoked")
    
    cert.status = "revoked"
    db.add(AuditLog(user_id=current_admin.id, action="REVOKE_CERT", timestamp=datetime.now(timezone.utc), details=f"Revoked certificate {cert.serial_number}"))
    db.commit()
    return {"message": "Certificate revoked"}

@router.post("/update-crl")
async def update_crl(req: RootCaRequest, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Tự động tạo danh sách CRL chứa các chứng chỉ đã thu hồi."""
    root_key_cfg = db.query(SystemConfig).filter(SystemConfig.config_key == "root_key_pem").first()
    root_cert_cfg = db.query(SystemConfig).filter(SystemConfig.config_key == "root_cert_pem").first()
    if not root_key_cfg or not root_cert_cfg:
        raise HTTPException(status_code=500, detail="Root CA not found")

    revoked_certs = db.query(Certificate).filter(Certificate.status == "revoked").all()
    serial_numbers = [int(cert.serial_number, 16) for cert in revoked_certs]

    try:
        crl_pem = generate_crl(
            revoked_serial_numbers=serial_numbers,
            root_key_pem_str=root_key_cfg.config_value,
            root_cert_pem_str=root_cert_cfg.config_value,
            root_password=req.password
        )
        
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "latest_crl_pem").first()
        if config:
            config.config_value = crl_pem
        else:
            db.add(SystemConfig(config_key="latest_crl_pem", config_value=crl_pem))
            
        db.add(AuditLog(user_id=current_admin.id, action="UPDATE_CRL", timestamp=datetime.now(timezone.utc)))
        db.commit()
        return {"message": "CRL updated successfully", "crl_pem": crl_pem}
    except Exception as e:
        db.rollback()  # Fix #13
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/audit-logs")
async def get_audit_logs(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Xem nhật ký hệ thống."""
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
