"""
File: backend/app/services/crypto/cert_issue.py
Description: Xử lý ký CSR, tạo Root CA và cấp phát chứng chỉ X.509
Fix #9: Verify CSR signature (proof-of-possession)
Fix #10: Thêm X.509v3 Extensions (SAN, KeyUsage, ExtendedKeyUsage)
Fix #11: Thay utcnow() bằng datetime.now(timezone.utc)
"""
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_root_ca(password: str, valid_days: int = 3650) -> tuple[str, str]:
    """Tạo Root CA (Self-signed) với đầy đủ Extensions."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "HCM"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Ho Chi Minh City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "X509 Local CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "X509 Local Root CA"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(timezone.utc)
    ).not_valid_after(
        datetime.now(timezone.utc) + timedelta(days=valid_days)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).add_extension(
        # Root CA cần quyền ký cert và CRL
        x509.KeyUsage(
            digital_signature=True, key_cert_sign=True, crl_sign=True,
            content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=False,
            encipher_only=False, decipher_only=False
        ), critical=True,
    ).add_extension(
        x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()), critical=False,
    ).sign(private_key, hashes.SHA256())

    encryption_algorithm = serialization.BestAvailableEncryption(password.encode("utf-8"))
    
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )
    
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    return key_pem.decode("utf-8"), cert_pem.decode("utf-8")


def sign_csr(csr_pem_str: str, root_key_pem_str: str, root_cert_pem_str: str, root_password: str, valid_days: int = 365) -> str:
    """Ký một CSR bằng Root CA — có verify signature và thêm Extensions."""
    csr = x509.load_pem_x509_csr(csr_pem_str.encode("utf-8"))
    
    # Fix #9: Verify CSR signature (proof-of-possession)
    if not csr.is_signature_valid:
        raise ValueError("CSR signature không hợp lệ — người gửi không sở hữu Private Key tương ứng.")
    
    root_cert = x509.load_pem_x509_certificate(root_cert_pem_str.encode("utf-8"))
    root_key = serialization.load_pem_private_key(
        root_key_pem_str.encode("utf-8"),
        password=root_password.encode("utf-8")
    )

    # Lấy Common Name từ CSR subject để tạo SAN
    cn_attrs = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    san_names = []
    if cn_attrs:
        cn_value = cn_attrs[0].value
        san_names.append(x509.DNSName(cn_value))

    builder = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        root_cert.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(timezone.utc)
    ).not_valid_after(
        datetime.now(timezone.utc) + timedelta(days=valid_days)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    ).add_extension(
        # Fix #10: Key Usage cho SSL/TLS end-entity cert
        x509.KeyUsage(
            digital_signature=True, key_encipherment=True,
            content_commitment=False, data_encipherment=False,
            key_agreement=False, key_cert_sign=False,
            crl_sign=False, encipher_only=False, decipher_only=False
        ), critical=True,
    ).add_extension(
        # Fix #10: Extended Key Usage cho SSL Server Authentication
        x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
        critical=False,
    )

    # Fix #10: Subject Alternative Name (SAN) — Bắt buộc cho HTTPS hiện đại
    if san_names:
        builder = builder.add_extension(
            x509.SubjectAlternativeName(san_names),
            critical=False,
        )

    cert = builder.sign(root_key, hashes.SHA256())
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
