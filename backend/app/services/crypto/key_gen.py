"""
File: backend/app/services/crypto/key_gen.py
Description: Cung cấp các hàm sinh cặp khóa bất đối xứng và mã hóa bảo vệ khóa riêng.
"""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(password: str, key_size: int = 2048) -> tuple[str, str]:
    """
    Sinh cặp khóa RSA. Private Key được mã hóa bằng AES-256 (PBKDF2) dùng password.
    Trả về tuple: (private_key_pem_string, public_key_pem_string)
    """
    # 1. Sinh khóa RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()

    # 2. Định dạng mã hóa cho Private Key
    # Sử dụng chuẩn BestAvailableEncryption (thường là AES-256) với PBKDF2 hashing
    encryption_algorithm = serialization.BestAvailableEncryption(password.encode("utf-8"))

    # 3. Serialize Private Key thành PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )

    # 4. Serialize Public Key thành PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode("utf-8"), public_pem.decode("utf-8")
