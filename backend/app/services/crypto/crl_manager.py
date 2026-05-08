import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization

def _get_hash_algorithm(hash_alg: str) -> hashes.HashAlgorithm:
    alg_map = {
        "sha256": hashes.SHA256(),
        "sha384": hashes.SHA384(),
        "sha512": hashes.SHA512(),
    }
    alg = alg_map.get(hash_alg.lower())
    if not alg:
        raise ValueError(f"Unsupported hash algorithm: {hash_alg}")
    return alg

def build_crl(
    root_cert_pem: str, 
    root_key_pem: str, 
    revoked_certs: list[dict], 
    days_to_next_update: int = 7,
    hash_alg: str = "sha256",
    **kwargs
) -> str:
    """
    Build a Certificate Revocation List (CRL).
    
    Args:
        root_cert_pem (str): The Root CA certificate in PEM format.
        root_key_pem (str): The Root CA private key in PEM format.
        revoked_certs (list[dict]): A list of dictionaries containing revoked certificate info.
            Each dict should have:
                - serial_number (int)
                - revocation_date (datetime.datetime)
        days_to_next_update (int): Days until the next CRL update.
        hash_alg (str): Hash algorithm for signing.
        **kwargs: Additional parameters.
        
    Returns:
        str: The generated CRL in PEM format.
    """
    from .key_gen import load_private_key
    
    root_cert = x509.load_pem_x509_certificate(root_cert_pem.encode('utf-8'))
    root_key = load_private_key(root_key_pem)
    
    builder = x509.CertificateRevocationListBuilder()
    builder = builder.issuer_name(root_cert.subject)
    
    now = datetime.datetime.now(datetime.timezone.utc)
    builder = builder.last_update(now)
    builder = builder.next_update(now + datetime.timedelta(days=days_to_next_update))
    
    for r_cert in revoked_certs:
        serial_number = int(r_cert.get("serial_number"))
        revocation_date = r_cert.get("revocation_date")
        if not isinstance(revocation_date, datetime.datetime):
            # Fallback if provided as ISO string
            if isinstance(revocation_date, str):
                revocation_date = datetime.datetime.fromisoformat(revocation_date)
            else:
                revocation_date = now
                
        revoked_builder = x509.RevokedCertificateBuilder()
        revoked_builder = revoked_builder.serial_number(serial_number)
        revoked_builder = revoked_builder.revocation_date(revocation_date)
        
        # Add to CRL builder
        builder = builder.add_revoked_certificate(revoked_builder.build())
        
    crl = builder.sign(root_key, _get_hash_algorithm(hash_alg))
    return crl.public_bytes(serialization.Encoding.PEM).decode('utf-8')

def parse_crl(crl_pem: str) -> dict:
    """
    Parse a Certificate Revocation List (CRL) and return its information.
    
    Args:
        crl_pem (str): The CRL in PEM format.
        
    Returns:
        dict: A dictionary containing CRL details.
    """
    crl = x509.load_pem_x509_crl(crl_pem.encode('utf-8'))
    
    def get_name_attributes(name: x509.Name) -> dict:
        result = {}
        for attribute in name:
            oid = attribute.oid
            from cryptography.x509.oid import NameOID
            if oid == NameOID.COMMON_NAME: result['CN'] = attribute.value
            elif oid == NameOID.ORGANIZATION_NAME: result['O'] = attribute.value
            elif oid == NameOID.ORGANIZATIONAL_UNIT_NAME: result['OU'] = attribute.value
            elif oid == NameOID.COUNTRY_NAME: result['C'] = attribute.value
        return result
        
    revoked_list = []
    for r in crl:
        revoked_list.append({
            "serial_number": str(r.serial_number),
            "revocation_date": r.revocation_date_utc.isoformat()
        })
        
    info = {
        "issuer": get_name_attributes(crl.issuer),
        "last_update": crl.last_update_utc.isoformat(),
        "next_update": crl.next_update_utc.isoformat(),
        "revoked_certificates": revoked_list
    }
    return info

def schedule_crl_update():
    """
    TODO: Lên lịch tự động cập nhật CRL mỗi 7 ngày.
    
    Hướng dẫn tích hợp:
    Bạn có thể dùng thư viện `apscheduler` trong FastAPI (trong `main.py`)
    để tự động chạy hàm này.
    
    Ví dụ:
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_crl_update, 'interval', days=7)
    scheduler.start()
    """
    print("Running scheduled CRL update...")
    # Lấy thông tin Root CA từ DB/KeyVault
    # Truy vấn danh sách các chứng chỉ đã thu hồi từ DB
    # crl_pem = build_crl(root_cert_pem, root_key_pem, revoked_certs, days_to_next_update=7)
    # Lưu crl_pem vào file hoặc DB để web server phục vụ tại URL CDP.
    pass
