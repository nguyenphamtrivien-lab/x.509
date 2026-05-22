from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime

from app.database import get_db
from app.models.models import User, CertRequest, Certificate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

# ==========================================
# ADMIN ROLE VERIFICATION
# ==========================================
def get_admin_user(current_user: User = Depends(get_current_user)):
    """Check if the current logged-in user has admin privileges"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. Administrator privileges required."
        )
    return current_user

# ==========================================
# API ENDPOINTS
# ==========================================

@router.get("/requests/pending")
async def get_pending_requests(
    admin: User = Depends(get_admin_user), 
    db: Session = Depends(get_db)
):
    """Retrieve all pending Certificate Signing Requests (CSR)"""
    requests = db.query(CertRequest).filter(CertRequest.status == "Pending").all()
    if not requests:
        return {"message": "No pending CSRs found at this time."}
    return requests

@router.post("/requests/{req_id}/approve")
async def approve_request(
    req_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Approve a CSR and issue an X.509 certificate"""
    
    req = db.query(CertRequest).filter(CertRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Certificate request not found.")
    if req.status != "Pending":
        raise HTTPException(status_code=400, detail="This request has already been processed.")

    req.status = "Approved"

    # MOCK CERTIFICATE GENERATION
    new_cert = Certificate(
        user_id=req.user_id,
        serial_number=f"SN-{req.id}-{int(datetime.datetime.now().timestamp())}",
        subject="Pending extraction from CSR", 
        issuer="KHTN CA",
        valid_from=datetime.datetime.utcnow(),
        valid_to=datetime.datetime.utcnow() + datetime.timedelta(days=365),
        status="Active",
        pem_data="-----BEGIN CERTIFICATE-----\n(M1_WILL_INJECT_REAL_SIGNATURE_HERE)\n-----END CERTIFICATE-----"
    )
    
    db.add(new_cert)
    db.commit()

    return {
        "message": f"Successfully approved request #{req_id}.", 
        "cert_serial": new_cert.serial_number
    }

@router.post("/certificates/{serial_number}/revoke")
async def revoke_certificate(
    serial_number: str,
    reason: str = "Key Compromise", 
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke an X.509 certificate by its Serial Number"""
    
    cert = db.query(Certificate).filter(Certificate.serial_number == serial_number).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate with the specified serial number not found.")
    
    if cert.status == "Revoked":
        raise HTTPException(status_code=400, detail="This certificate has already been revoked.")

    cert.status = "Revoked"
    
    db.commit()

    return {
        "message": "Certificate successfully revoked.",
        "serial_number": serial_number,
        "new_status": cert.status,
        "reason": reason
    }