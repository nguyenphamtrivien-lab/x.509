from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import datetime

from app.database import get_db
from app.models.models import Certificate

router = APIRouter(tags=["Public API"])

@router.get("/crl")
async def get_certificate_revocation_list(db: Session = Depends(get_db)):
    """
    Export the Certificate Revocation List (CRL).
    Public endpoint accessible without authentication.
    """
    revoked_certs = db.query(Certificate).filter(Certificate.status == "Revoked").all()
    
    revoked_list = []
    for cert in revoked_certs:
        revoked_list.append({
            "serial_number": cert.serial_number,
            "revocation_date": datetime.datetime.utcnow().isoformat()
        })
    
    return {
        "issuer": "KHTN CA",
        "last_update": datetime.datetime.utcnow().isoformat(),
        "next_update": (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat(),
        "revoked_certificates": revoked_list
    }

@router.get("/ocsp/{serial_number}")
async def check_certificate_status(serial_number: str, db: Session = Depends(get_db)):
    """
    Online Certificate Status Protocol (OCSP) endpoint:
    Check the current status (Good, Revoked, Unknown) of a specific certificate.
    """
    cert = db.query(Certificate).filter(Certificate.serial_number == serial_number).first()
    
    if not cert:
        return {
            "serial_number": serial_number,
            "status": "Unknown",
            "message": "Certificate not found in the system."
        }
    
    ocsp_status = "Good" if cert.status == "Active" else "Revoked"
    
    return {
        "serial_number": serial_number,
        "status": ocsp_status,
        "check_time": datetime.datetime.utcnow().isoformat()
    }