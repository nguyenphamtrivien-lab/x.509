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

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from app.services.crypto import key_gen

router = APIRouter(prefix="/customer", tags=["Customer"])

class KeyGenRequest(BaseModel):
    key_type: str = "RSA" # "RSA" or "EC"
    key_size_or_curve: str = "2048" # e.g., "2048" for RSA, "secp256r1" for EC
    password: str

class KeyGenResponse(BaseModel):
    public_key: str
    encrypted_private_key: str

@router.post("/gen-keypair", response_model=KeyGenResponse)
async def gen_keypair(request: KeyGenRequest):
    """
    Generate a new RSA/EC keypair for a customer.
    The private key is protected via AES using the provided password.
    """
    try:
        if request.key_type.upper() == "RSA":
            priv_pem, pub_pem = key_gen.generate_rsa_keypair(int(request.key_size_or_curve))
        elif request.key_type.upper() == "EC":
            priv_pem, pub_pem = key_gen.generate_ec_keypair(request.key_size_or_curve)
        else:
            raise HTTPException(status_code=400, detail="Invalid key type. Use 'RSA' or 'EC'.")
            
        # The key is currently unencrypted in memory, load it to export with password
        priv_key_obj = key_gen.load_private_key(priv_pem)
        encrypted_priv_pem = key_gen.export_private_key_with_password(priv_key_obj, request.password)
        
        return KeyGenResponse(
            public_key=pub_pem,
            encrypted_private_key=encrypted_priv_pem
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
