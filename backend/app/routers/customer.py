"""
File: backend/app/routers/customer.py
Description: Customer endpoints for requesting and managing certificates.
Fix #1: Validate CSR trước khi lưu DB
Fix #12: Chạy RSA gen trong thread pool (non-blocking)
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from app.database import get_db
from app.models.models import User, CertRequest, Certificate, SystemConfig
from app.dependencies import get_current_user
from app.services.crypto.key_gen import generate_rsa_keypair

router = APIRouter(prefix="/customer", tags=["Customer"])
executor = ThreadPoolExecutor(max_workers=2)

class KeyGenRequest(BaseModel):
    password: str

class CsrSubmitRequest(BaseModel):
    csr_pem: str

class DecodeCertRequest(BaseModel):
    cert_pem: str

@router.post("/gen-keypair")
async def gen_keypair(req: KeyGenRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a new RSA keypair. Fix #12: Non-blocking."""
    try:
        key_size_cfg = db.query(SystemConfig).filter(SystemConfig.config_key == "client_key_size").first()
        key_size = int(key_size_cfg.config_value) if key_size_cfg else 2048
        
        loop = asyncio.get_event_loop()
        priv_pem, pub_pem = await loop.run_in_executor(
            executor, generate_rsa_keypair, req.password, key_size
        )
        return {"private_key": priv_pem, "public_key": pub_pem}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/submit-csr")
async def submit_csr(req: CsrSubmitRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Submit a Certificate Signing Request. Fix #1: Validate CSR trước."""
    # Fix #1: Validate CSR format trước khi lưu vào DB
    try:
        from cryptography import x509
        csr_obj = x509.load_pem_x509_csr(req.csr_pem.encode('utf-8'))
    except Exception:
        raise HTTPException(status_code=400, detail="CSR không hợp lệ. Vui lòng kiểm tra lại định dạng PEM.")

    new_request = CertRequest(
        user_id=current_user.id,
        csr_data=req.csr_pem,
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return {"message": "CSR submitted successfully", "request_id": new_request.id}

@router.get("/csr-requests")
async def list_csr_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xem danh sách yêu cầu cấp phát chứng chỉ và trạng thái."""
    return db.query(CertRequest).filter(CertRequest.user_id == current_user.id).order_by(CertRequest.created_at.desc()).all()

@router.get("/certs")
async def list_certs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all certificates for the current user."""
    return db.query(Certificate).filter(Certificate.user_id == current_user.id).all()

@router.post("/certs/{cert_id}/request-revoke")
async def request_revoke(cert_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Request revocation of a certificate."""
    cert = db.query(Certificate).filter(Certificate.id == cert_id, Certificate.user_id == current_user.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if cert.status == "revoked":
        raise HTTPException(status_code=400, detail="Already revoked")
    if cert.status == "revoke_pending":
        raise HTTPException(status_code=400, detail="Revocation already requested")
    cert.status = "revoke_pending"
    db.commit()
    return {"message": "Revocation requested"}

@router.get("/certs/{cert_id}/download")
async def download_cert(cert_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Tải file chứng chỉ về máy."""
    cert = db.query(Certificate).filter(Certificate.id == cert_id, Certificate.user_id == current_user.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    return Response(content=cert.pem_data, media_type="application/x-pem-file", headers={
        "Content-Disposition": f"attachment; filename=certificate_{cert.serial_number}.crt"
    })

@router.post("/certs/decode")
async def decode_cert(req: DecodeCertRequest):
    """Upload một chứng chỉ bất kỳ dưới dạng PEM để xem thông tin."""
    try:
        from cryptography import x509
        cert_obj = x509.load_pem_x509_certificate(req.cert_pem.encode('utf-8'))
        
        # Trích xuất thông tin chi tiết
        extensions_info = []
        for ext in cert_obj.extensions:
            extensions_info.append({
                "oid": ext.oid.dotted_string,
                "name": ext.oid._name,
                "critical": ext.critical,
                "value": str(ext.value)
            })

        return {
            "serial_number": format(cert_obj.serial_number, 'x'),
            "subject": str(cert_obj.subject),
            "issuer": str(cert_obj.issuer),
            "valid_from": cert_obj.not_valid_before_utc.isoformat(),
            "valid_to": cert_obj.not_valid_after_utc.isoformat(),
            "signature_algorithm": cert_obj.signature_algorithm_oid._name,
            "public_key_size": cert_obj.public_key().key_size,
            "extensions": extensions_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Certificate PEM: {str(e)}")

@router.get("/crl")
async def get_crl(db: Session = Depends(get_db)):
    """Tra cứu danh sách CRL của hệ thống."""
    crl_config = db.query(SystemConfig).filter(SystemConfig.config_key == "latest_crl_pem").first()
    if not crl_config:
        raise HTTPException(status_code=404, detail="CRL not found or not generated yet")
    return Response(content=crl_config.config_value, media_type="application/x-pem-file")
