"""
File: backend/app/services/crypto/crl_manager.py
Description: Xử lý tạo và quản lý Certificate Revocation List (CRL).
Fix #11: Thay utcnow() bằng datetime.now(timezone.utc)
"""
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

def generate_crl(revoked_serial_numbers: list[int], root_key_pem_str: str, root_cert_pem_str: str, root_password: str) -> str:
    """Tạo file CRL chứa danh sách các serial number bị thu hồi."""
    root_cert = x509.load_pem_x509_certificate(root_cert_pem_str.encode("utf-8"))
    root_key = serialization.load_pem_private_key(
        root_key_pem_str.encode("utf-8"),
        password=root_password.encode("utf-8")
    )
    
    builder = x509.CertificateRevocationListBuilder()
    builder = builder.issuer_name(root_cert.subject)
    builder = builder.last_update(datetime.now(timezone.utc))
    builder = builder.next_update(datetime.now(timezone.utc) + timedelta(days=1))
    
    for serial in revoked_serial_numbers:
        revoked_cert = x509.RevokedCertificateBuilder().serial_number(
            serial
        ).revocation_date(
            datetime.now(timezone.utc)
        ).build()
        builder = builder.add_revoked_certificate(revoked_cert)
        
    crl = builder.sign(
        private_key=root_key, algorithm=hashes.SHA256()
    )
    
    return crl.public_bytes(serialization.Encoding.PEM).decode("utf-8")
