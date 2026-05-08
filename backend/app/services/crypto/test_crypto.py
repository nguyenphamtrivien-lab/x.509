import os
import sys
import datetime

# Add backend dir to sys.path so we can import as if we are in backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.services.crypto.key_gen import generate_rsa_keypair, generate_ec_keypair, load_private_key, export_private_key_with_password
from app.services.crypto.cert_issue import generate_root_ca, sign_csr, parse_cert_info
from app.services.crypto.crl_manager import build_crl, parse_crl
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

def create_mock_csr(private_pem: str) -> str:
    from cryptography.hazmat.primitives import serialization
    private_key = load_private_key(private_pem)
    builder = x509.CertificateSigningRequestBuilder()
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "mock.customer.com"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Customer Org"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
    ]))
    builder = builder.add_extension(
        x509.SubjectAlternativeName([x509.DNSName("mock.customer.com")]),
        critical=False,
    )
    csr = builder.sign(private_key, hashes.SHA256())
    return csr.public_bytes(serialization.Encoding.PEM).decode('utf-8')

def run_tests():
    print("1. Testing Key Generation...")
    rsa_priv, rsa_pub = generate_rsa_keypair(2048)
    ec_priv, ec_pub = generate_ec_keypair("secp256r1")
    assert "BEGIN PRIVATE KEY" in rsa_priv
    assert "BEGIN PUBLIC KEY" in rsa_pub
    assert "BEGIN PRIVATE KEY" in ec_priv
    
    print("2. Testing Password Export...")
    loaded_key = load_private_key(rsa_priv)
    encrypted_priv = export_private_key_with_password(loaded_key, "supersecret")
    assert "ENCRYPTED PRIVATE KEY" in encrypted_priv
    
    print("3. Testing Root CA Generation...")
    root_cert_pem, root_key_pem = generate_root_ca("My Root CA Org", "VN", 2048, 365, "sha256")
    assert "BEGIN CERTIFICATE" in root_cert_pem
    
    print("4. Testing CSR and Issuance...")
    cust_priv, cust_pub = generate_rsa_keypair(2048)
    csr_pem = create_mock_csr(cust_priv)
    issued_cert, chain = sign_csr(
        csr_pem=csr_pem,
        root_cert_pem=root_cert_pem,
        root_key_pem=root_key_pem,
        validity_days=90,
        hash_alg="sha256",
        ocsp_url="http://ocsp.myca.local",
        crl_url="http://crl.myca.local/latest.crl"
    )
    assert "BEGIN CERTIFICATE" in issued_cert
    
    print("5. Testing Certificate Parsing...")
    info = parse_cert_info(issued_cert)
    assert info["subject"].get("CN") == "mock.customer.com"
    assert "mock.customer.com" in info["san"]
    
    print("6. Testing CRL Generation...")
    revoked = [
        {
            "serial_number": info["serial_number"],
            "revocation_date": datetime.datetime.now(datetime.timezone.utc)
        }
    ]
    crl_pem = build_crl(root_cert_pem, root_key_pem, revoked, days_to_next_update=7)
    assert "BEGIN X509 CRL" in crl_pem
    
    print("7. Testing CRL Parsing...")
    crl_info = parse_crl(crl_pem)
    assert len(crl_info["revoked_certificates"]) == 1
    assert crl_info["revoked_certificates"][0]["serial_number"] == info["serial_number"]
    
    print("All tests passed successfully!")

if __name__ == "__main__":
    run_tests()
