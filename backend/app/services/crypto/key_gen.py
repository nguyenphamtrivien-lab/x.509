from typing import Any
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(key_size: int = 2048) -> tuple[str, str]:
    """
    Generate an RSA key pair.
    
    Args:
        key_size (int): The size of the RSA key.
        
    Returns:
        tuple[str, str]: (private_pem, public_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem

def generate_ec_keypair(curve: str = "secp256r1") -> tuple[str, str]:
    """
    Generate an Elliptic Curve (EC) key pair.
    
    Args:
        curve (str): The name of the curve.
        
    Returns:
        tuple[str, str]: (private_pem, public_pem)
    """
    curve_map = {
        "secp256r1": ec.SECP256R1(),
        "secp384r1": ec.SECP384R1(),
        "secp521r1": ec.SECP521R1(),
    }
    
    selected_curve = curve_map.get(curve.lower())
    if not selected_curve:
        raise ValueError(f"Unsupported curve: {curve}")
        
    private_key = ec.generate_private_key(selected_curve)
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem

def load_private_key(pem: str, password: str = None) -> Any:
    """
    Load a private key from a PEM string.
    
    Args:
        pem (str): The private key in PEM format.
        password (str): Password for decryption, if encrypted.
        
    Returns:
        Any: The loaded private key object.
    """
    pwd_bytes = password.encode('utf-8') if password else None
    return serialization.load_pem_private_key(
        pem.encode('utf-8'),
        password=pwd_bytes
    )

def export_private_key_with_password(private_key: Any, password: str) -> str:
    """
    Export a private key to PEM format with password encryption.
    
    Args:
        private_key (Any): The private key object (RSA or EC).
        password (str): The password to encrypt the key.
        
    Returns:
        str: Password-encrypted private key in PEM format.
    """
    encryption_algorithm = serialization.BestAvailableEncryption(password.encode('utf-8'))
    
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )
    return pem_bytes.decode('utf-8')
