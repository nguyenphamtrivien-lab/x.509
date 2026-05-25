"""
File: helper_gen_csr.py
Description: Tiện ích hỗ trợ sinh cặp khóa RSA và yêu cầu ký số CSR nhanh chóng để test dự án X.509.
"""
import os
import sys

# Kiểm tra sự tồn tại của thư viện cryptography
try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("[-] Thư viện 'cryptography' chưa được cài đặt.")
    print("[*] Vui lòng kích hoạt virtual environment và cài đặt:")
    print("    Windows (CMD): .venv\\Scripts\\activate && pip install cryptography")
    print("    Windows (PowerShell): .\\.venv\\Scripts\\Activate.ps1 && pip install cryptography")
    sys.exit(1)

def main():
    print("=" * 60)
    print("     CÔNG CỤ TẠO CẶP KHÓA & CSR ĐỂ TEST HỆ THỐNG X.509")
    print("=" * 60)
    
    # Nhập thông tin
    common_name = input("1. Nhập Common Name (Tên miền, ví dụ: myweb.com): ").strip()
    if not common_name:
        common_name = "example.com"
        print(f"   -> Sử dụng mặc định: {common_name}")
        
    org_name = input("2. Nhập Tên Tổ chức (ví dụ: Truong DH Bach Khoa): ").strip()
    if not org_name:
        org_name = "HUST"
        print(f"   -> Sử dụng mặc định: {org_name}")
        
    password = input("3. Nhập Mật khẩu bảo vệ Private Key (tối thiểu 4 ký tự): ").strip()
    while len(password) < 4:
        password = input("   Mật khẩu quá ngắn, vui lòng nhập lại: ").strip()

    print("\n[*] Đang khởi tạo cặp khóa RSA 2048-bit...")
    # 1. Sinh khóa RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # 2. Mã hóa Private Key bằng mật khẩu người dùng nhập
    encryption_algorithm = serialization.BestAvailableEncryption(password.encode('utf-8'))
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )
    
    # 3. Xuất Public Key dạng PEM
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    print("[*] Đang ký số và tạo CSR...")
    # 4. Tạo CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"VN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Hanoi"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Hai Ba Trung"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_name),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name),
            x509.DNSName(f"www.{common_name}"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    
    # 5. Lưu ra các file cục bộ
    output_dir = "test_credentials"
    os.makedirs(output_dir, exist_ok=True)
    
    priv_file = os.path.join(output_dir, "customer_private_key.pem")
    pub_file = os.path.join(output_dir, "customer_public_key.pem")
    csr_file = os.path.join(output_dir, "customer_csr.pem")
    
    with open(priv_file, "w", encoding="utf-8") as f:
        f.write(private_pem.decode('utf-8'))
    with open(pub_file, "w", encoding="utf-8") as f:
        f.write(public_pem.decode('utf-8'))
    with open(csr_file, "w", encoding="utf-8") as f:
        f.write(csr_pem)
        
    print("\n" + "="*50)
    print("[+] TẠO THÀNH CÔNG!")
    print(f"[-] Khóa riêng mã hóa (AES-256) đã lưu tại: {priv_file}")
    print(f"[-] Khóa công khai đã lưu tại: {pub_file}")
    print(f"[-] File yêu cầu CSR đã lưu tại: {csr_file}")
    print("="*50)
    print("\n>>> MÃ CSR PEM CỦA BẠN (HÃY COPY DÒNG DƯỚI ĐỂ DÁN VÀO WEB): <<<\n")
    print(csr_pem)
    print("="*50)
    print("Mẹo: Mở trang web (Customer Dashboard -> CSR Request) và dán nội dung trên để test.")
    print("="*50)

if __name__ == "__main__":
    main()
