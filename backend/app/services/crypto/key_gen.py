"""
File: backend/app/services/crypto/key_gen.py
Description: Cryptographic key generation utilities using cryptography (PyCA).
TODO:
- Implement RSA key generation with configurable size.
- Implement Elliptic Curve key generation with configurable curve.
- Add serialization to PEM format.
"""

def generate_rsa_keypair(key_size: int = 2048):
    """
    Generate an RSA private and public key pair.
    
    :param key_size: The size of the RSA key in bits.
    :return: Tuple of (private_key_pem, public_key_pem)
    """
    # TODO: Use cryptography.hazmat.primitives.asymmetric.rsa
    raise NotImplementedError("RSA key generation not implemented")

def generate_ec_keypair(curve_name: str = "secp256r1"):
    """
    Generate an Elliptic Curve private and public key pair.
    
    :param curve_name: The name of the elliptic curve to use.
    :return: Tuple of (private_key_pem, public_key_pem)
    """
    # TODO: Use cryptography.hazmat.primitives.asymmetric.ec
    raise NotImplementedError("EC key generation not implemented")
