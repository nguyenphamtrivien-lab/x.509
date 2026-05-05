"""
File: backend/app/routers/customer.py
Description: Customer endpoints for requesting and managing certificates.
TODO:
- Implement keypair generation on server (or instruct client).
- Implement CSR submission.
- Implement retrieving user's certificates.
- Implement certificate download.
- Implement certificate revocation request.
- Implement CRL retrieval.
- Add authentication dependency.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.post("/gen-keypair")
async def gen_keypair():
    """Generate a new RSA/EC keypair."""
    raise NotImplementedError()

@router.post("/submit-csr")
async def submit_csr():
    """Submit a Certificate Signing Request."""
    raise NotImplementedError()

@router.get("/certs")
async def list_certs():
    """List all certificates for the current user."""
    raise NotImplementedError()

@router.get("/certs/{cert_id}/download")
async def download_cert(cert_id: int):
    """Download an issued certificate."""
    raise NotImplementedError()

@router.post("/certs/{cert_id}/request-revoke")
async def request_revoke(cert_id: int):
    """Request revocation of a certificate."""
    raise NotImplementedError()

@router.get("/crl")
async def get_crl():
    """Get the current Certificate Revocation List."""
    raise NotImplementedError()
