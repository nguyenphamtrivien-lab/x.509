from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.models import User, CertRequest, Certificate
from app.routers.auth import get_current_user 

router = APIRouter(prefix="/customer", tags=["Customer"])

# ==========================================
# PYDANTIC SCHEMAS
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a Certificate Signing Request (CSR)"""
    new_request = CertRequest(
        user_id=current_user.id,
        csr_data=data.csr_data,
        status="Pending" 
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return {
        "message": "CSR successfully submitted.", 
        "request_id": new_request.id,
        "status": new_request.status
    }

@router.get("/certs")
async def list_certs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all certificates associated with the authenticated user"""
    certs = db.query(Certificate).filter(Certificate.user_id == current_user.id).all()
    if not certs:
        return {"message": "No certificates found for this account."}
    
    return certs

@router.post("/certs/{cert_id}/request-revoke")
async def request_revoke(
    cert_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a revocation request for a compromised certificate"""
    cert = db.query(Certificate).filter(
        Certificate.id == cert_id, 
        Certificate.user_id == current_user.id
    ).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    
    if cert.status == "Revoked":
        raise HTTPException(status_code=400, detail="This certificate is already revoked.")
    
    cert.status = "Revoke_Pending"
    db.commit()
    
    return {"message": "Revocation request successfully submitted. Pending admin approval."}

@router.get("/certificates")
async def get_my_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch all X.509 certificates issued to the current user"""
    certs = db.query(Certificate).filter(Certificate.user_id == current_user.id).all()
    
    if not certs:
        return {"message": "No issued certificates found."}
    
    return certs