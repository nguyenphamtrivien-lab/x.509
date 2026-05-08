import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from typing import Optional

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

def generate_root_ca(org: str, country: str, key_size: int, validity_days: int, hash_alg: str) -> tuple[str, str]:
    """
    Generate a self-signed Root Certificate Authority (CA).
    
    Args:
        org (str): The organization name.
        country (str): The country code.
        key_size (int): The RSA key size.
        validity_days (int): Validity period in days.
        hash_alg (str): Hash algorithm to use.
        
    Returns:
        tuple[str, str]: (root_cert_pem, root_key_pem)
    """
    from .key_gen import generate_rsa_keypair, load_private_key
    
    # Generate key for Root CA
    priv_pem, pub_pem = generate_rsa_keypair(key_size)
    private_key = load_private_key(priv_pem)
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, f"{org} Root CA"),
    ])
    
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(issuer)
    builder = builder.public_key(private_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(datetime.datetime.now(datetime.timezone.utc))
    builder = builder.not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=validity_days))
    
    # Basic Constraints: CA=True
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    )
    # Key Usage
    builder = builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    # Subject Key Identifier
    builder = builder.add_extension(
        x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
        critical=False,
    )
    
    cert = builder.sign(private_key, _get_hash_algorithm(hash_alg))
    
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    return cert_pem, priv_pem

def sign_csr(
    csr_pem: str, 
    root_cert_pem: str, 
    root_key_pem: str, 
    validity_days: int, 
    hash_alg: str,
    ocsp_url: Optional[str] = None,
    crl_url: Optional[str] = None
) -> tuple[str, str]:
    """
    Sign a Certificate Signing Request (CSR) with a Root CA.
    
    Args:
        csr_pem (str): The CSR in PEM format.
        root_cert_pem (str): The Root CA certificate in PEM format.
        root_key_pem (str): The Root CA private key in PEM format.
        validity_days (int): Validity period in days.
        hash_alg (str): Hash algorithm to use.
        ocsp_url (str, optional): URL for OCSP.
        crl_url (str, optional): URL for CRL Distribution Point.
        
    Returns:
        tuple[str, str]: (issued_cert_pem, certificate_chain)
    """
    from .key_gen import load_private_key
    
    csr = x509.load_pem_x509_csr(csr_pem.encode('utf-8'))
    if not csr.is_signature_valid:
        raise ValueError("Invalid CSR signature")
        
    root_cert = x509.load_pem_x509_certificate(root_cert_pem.encode('utf-8'))
    root_key = load_private_key(root_key_pem)
    
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(csr.subject)
    builder = builder.issuer_name(root_cert.subject)
    builder = builder.public_key(csr.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(datetime.datetime.now(datetime.timezone.utc))
    builder = builder.not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=validity_days))
    
    # Copy SAN from CSR if present
    try:
        san_ext = csr.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        builder = builder.add_extension(san_ext.value, critical=san_ext.critical)
    except x509.ExtensionNotFound:
        pass
        
    # Add Authority Key Identifier
    builder = builder.add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(root_cert.public_key()),
        critical=False,
    )
    
    # Subject Key Identifier
    builder = builder.add_extension(
        x509.SubjectKeyIdentifier.from_public_key(csr.public_key()),
        critical=False,
    )
    
    # Basic Constraints: CA=False
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )

    # Authority Information Access (OCSP)
    if ocsp_url:
        builder = builder.add_extension(
            x509.AuthorityInformationAccess([
                x509.AccessDescription(
                    x509.AuthorityInformationAccessOID.OCSP,
                    x509.UniformResourceIdentifier(ocsp_url)
                )
            ]),
            critical=False,
        )

    # CRL Distribution Points (CDP)
    if crl_url:
        builder = builder.add_extension(
            x509.CRLDistributionPoints([
                x509.DistributionPoint(
                    full_name=[x509.UniformResourceIdentifier(crl_url)],
                    relative_name=None,
                    reasons=None,
                    crl_issuer=None
                )
            ]),
            critical=False,
        )
        
    cert = builder.sign(root_key, _get_hash_algorithm(hash_alg))
    
    issued_cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    certificate_chain = issued_cert_pem + "\n" + root_cert_pem
    
    return issued_cert_pem, certificate_chain

def parse_cert_info(cert_pem: str) -> dict:
    """
    Parse an X.509 certificate and return its information.
    
    Args:
        cert_pem (str): The certificate in PEM format.
        
    Returns:
        dict: A dictionary containing certificate details.
    """
    cert = x509.load_pem_x509_certificate(cert_pem.encode('utf-8'))
    
    def get_name_attributes(name: x509.Name) -> dict:
        result = {}
        for attribute in name:
            oid = attribute.oid
            if oid == NameOID.COMMON_NAME: result['CN'] = attribute.value
            elif oid == NameOID.ORGANIZATION_NAME: result['O'] = attribute.value
            elif oid == NameOID.ORGANIZATIONAL_UNIT_NAME: result['OU'] = attribute.value
            elif oid == NameOID.COUNTRY_NAME: result['C'] = attribute.value
        return result

    sans = []
    try:
        san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        for name in san_ext.value:
            if isinstance(name, x509.DNSName):
                sans.append(name.value)
    except x509.ExtensionNotFound:
        pass

    info = {
        "serial_number": str(cert.serial_number),
        "subject": get_name_attributes(cert.subject),
        "issuer": get_name_attributes(cert.issuer),
        "not_valid_before": cert.not_valid_before_utc.isoformat(),
        "not_valid_after": cert.not_valid_after_utc.isoformat(),
        "san": sans
    }
    return info

def renew_cert(
    cert_pem: str, 
    root_key_pem: str, 
    new_validity_days: int, 
    hash_alg: str = "sha256"
) -> str:
    """
    Renew an existing certificate by signing a new one with the same subject and public key,
    but with a new validity period.
    
    Args:
        cert_pem (str): The existing certificate in PEM format.
        root_key_pem (str): The Root CA private key in PEM format to sign the renewed cert.
        new_validity_days (int): The new validity period in days.
        hash_alg (str): Hash algorithm to use.
        
    Returns:
        str: The renewed certificate in PEM format.
    """
    from .key_gen import load_private_key
    
    cert = x509.load_pem_x509_certificate(cert_pem.encode('utf-8'))
    root_key = load_private_key(root_key_pem)
    
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(cert.subject)
    builder = builder.issuer_name(cert.issuer)
    builder = builder.public_key(cert.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(datetime.datetime.now(datetime.timezone.utc))
    builder = builder.not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=new_validity_days))
    
    # Copy all extensions from the old certificate (SAN, AIA, CDP, etc.)
    for ext in cert.extensions:
        builder = builder.add_extension(ext.value, critical=ext.critical)
        
    renewed_cert = builder.sign(root_key, _get_hash_algorithm(hash_alg))
    return renewed_cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
