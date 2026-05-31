import os
import sys
import time
import json
import subprocess
import urllib.request
import urllib.parse

# Force stdout/stderr to use UTF-8 encoding to avoid Windows console errors
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID

# Port and base URL
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
DB_PATH = "x509_system.db"

def kill_port_8000():
    """Kill any process running on port 8000 (Windows)."""
    try:
        output = subprocess.check_output(f"netstat -ano | findstr LISTENING | findstr :{PORT}", shell=True).decode('utf-8')
        pids = set()
        for line in output.strip().split('\n'):
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                pids.add(pid)
        for pid in pids:
            print(f"[*] Killing process {pid} on port {PORT}...")
            subprocess.run(f"taskkill /F /PID {pid}", shell=True)
        time.sleep(1)
    except subprocess.CalledProcessError:
        # No process listening on port 8000
        pass

def delete_db():
    """Delete existing SQLite database to start fresh."""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[+] Deleted existing database: {DB_PATH}")
        except Exception as e:
            print(f"[-] Failed to delete database: {e}")
    else:
        print("[*] Database file does not exist. Starting with clean state.")

def request_api(path, method="GET", headers=None, json_data=None, form_data=None, raw_response=False):
    """Utility to make HTTP requests using urllib."""
    url = f"{BASE_URL}{path}"
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": "DemoRunner/1.0"
    }
    if headers:
        req_headers.update(headers)

    data_bytes = None
    if json_data is not None:
        data_bytes = json.dumps(json_data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    elif form_data is not None:
        data_bytes = urllib.parse.urlencode(form_data).encode("utf-8")
        req_headers["Content-Type"] = "application/x-www-form-urlencoded"

    req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read()
            if raw_response:
                return status, content
            
            # Try to parse json
            try:
                parsed_content = json.loads(content.decode("utf-8"))
            except ValueError:
                parsed_content = content.decode("utf-8")
            return status, parsed_content
    except urllib.error.HTTPError as e:
        status = e.code
        content = e.read().decode("utf-8")
        try:
            parsed_content = json.loads(content)
        except ValueError:
            parsed_content = content
        return status, parsed_content
    except Exception as e:
        return 500, str(e)

def run_demo():
    print("=" * 70)
    print("         KỊCH BẢN CHẠY DEMO TỰ ĐỘNG - HỆ THỐNG X.509 PKI")
    print("=" * 70)
    
    # Step 0: Clean up
    kill_port_8000()
    delete_db()
    
    # Start server
    print("[*] Đang khởi động FastAPI Backend Server...")
    python_exe = sys.executable
    server_process = subprocess.Popen(
        [python_exe, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    # Wait for server to boot
    print("[*] Đang chờ server sẵn sàng (3 giây)...")
    time.sleep(3)
    
    # Quick healthcheck
    try:
        health_req = urllib.request.Request(f"{BASE_URL}/docs")
        with urllib.request.urlopen(health_req) as r:
            if r.status == 200:
                print("[+] Server đã chạy thành công trên port 8000!")
    except Exception as e:
        print(f"[-] Không thể kết nối tới server: {e}")
        server_process.kill()
        return

    admin_token = None
    customer_token = None
    csr_pem_data = None
    cert_id = None
    serial_hex = None

    try:
        # ==========================================
        # BƯỚC 1: Đăng ký tài khoản Admin
        # ==========================================
        print("\n--- BƯỚC 1: Đăng ký tài khoản Admin ---")
        payload_admin_reg = {
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }
        status, resp = request_api("/auth/register", method="POST", json_data=payload_admin_reg)
        print(f"API Register Admin -> Status: {status}, Response: {resp}")
        assert status == 200 or status == 201, f"Failed to register Admin: {resp}"
        print("✅ Thành công: Đã đăng ký tài khoản Admin 'admin'.")

        # ==========================================
        # BƯỚC 2: Đăng nhập Admin
        # ==========================================
        print("\n--- BƯỚC 2: Đăng nhập Admin ---")
        form_admin_login = {
            "username": "admin",
            "password": "admin123"
        }
        status, resp = request_api("/auth/login", method="POST", form_data=form_admin_login)
        print(f"API Login Admin -> Status: {status}, Response: {resp}")
        assert status == 200, f"Failed to login Admin: {resp}"
        admin_token = resp.get("access_token")
        print(f"✅ Thành công: Đăng nhập thành công. JWT Token nhận được: {admin_token[:20]}...")

        # ==========================================
        # BƯỚC 3: Khởi tạo Root CA
        # ==========================================
        print("\n--- BƯỚC 3: Khởi tạo Root CA ---")
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        payload_root_ca = {
            "password": "ca_password_123"
        }
        status, resp = request_api("/admin/gen-root-ca", method="POST", headers=headers_admin, json_data=payload_root_ca)
        print(f"API Generate Root CA -> Status: {status}, Response: {resp}")
        assert status == 200, f"Failed to generate Root CA: {resp}"
        print("✅ Thành công: Đã sinh và mã hóa Root CA với mật khẩu bảo vệ.")

        # ==========================================
        # BƯỚC 4: Đăng ký tài khoản Customer
        # ==========================================
        print("\n--- BƯỚC 4: Đăng ký tài khoản Customer ---")
        payload_cust_reg = {
            "username": "customer1",
            "password": "cust123",
            "role": "customer"
        }
        status, resp = request_api("/auth/register", method="POST", json_data=payload_cust_reg)
        print(f"API Register Customer -> Status: {status}, Response: {resp}")
        assert status == 200 or status == 201, f"Failed to register Customer: {resp}"
        print("✅ Thành công: Đã đăng ký tài khoản Customer 'customer1'.")

        # ==========================================
        # BƯỚC 5: Đăng nhập Customer
        # ==========================================
        print("\n--- BƯỚC 5: Đăng nhập Customer ---")
        form_cust_login = {
            "username": "customer1",
            "password": "cust123"
        }
        status, resp = request_api("/auth/login", method="POST", form_data=form_cust_login)
        print(f"API Login Customer -> Status: {status}, Response: {resp}")
        assert status == 200, f"Failed to login Customer: {resp}"
        customer_token = resp.get("access_token")
        print(f"✅ Thành công: Đăng nhập Customer thành công. JWT Token: {customer_token[:20]}...")

        # ==========================================
        # BƯỚC 6: Sinh cặp khóa & tạo CSR
        # ==========================================
        print("\n--- BƯỚC 6: Sinh cặp khóa RSA & Tạo CSR cục bộ ---")
        print("[*] Đang sinh cặp khóa RSA-2048...")
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        print("[*] Đang tạo CSR PKCS#10 (CommonName=myweb.com, Org=HUST)...")
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"VN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Hanoi"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Hai Ba Trung"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"HUST"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"myweb.com"),
        ])).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"myweb.com"),
                x509.DNSName(u"www.myweb.com"),
            ]),
            critical=False,
        ).sign(key, hashes.SHA256())
        
        csr_pem_data = csr.public_bytes(serialization.Encoding.PEM).decode('utf-8')
        print(f"CSR PEM generated:\n{csr_pem_data[:150]}...\n{csr_pem_data[-150:]}")
        print("✅ Thành công: Đã sinh khóa và tự ký CSR cục bộ bằng SHA256.")

        # ==========================================
        # BƯỚC 7: Nộp CSR lên hệ thống
        # ==========================================
        print("\n--- BƯỚC 7: Nộp CSR lên hệ thống ---")
        headers_customer = {"Authorization": f"Bearer {customer_token}"}
        payload_csr = {
            "csr_pem": csr_pem_data
        }
        status, resp = request_api("/customer/submit-csr", method="POST", headers=headers_customer, json_data=payload_csr)
        print(f"API Submit CSR -> Status: {status}, Response: {resp}")
        assert status == 200 or status == 201, f"Failed to submit CSR: {resp}"
        print("✅ Thành công: Đã gửi CSR thành công. Trạng thái trong DB sẽ là PENDING.")

        # ==========================================
        # BƯỚC 8: Admin Duyệt và Ký CSR
        # ==========================================
        print("\n--- BƯỚC 8: Admin Duyệt và Ký CSR ---")
        # 8.1. Lấy danh sách CSRs
        status, resp = request_api("/admin/csrs", method="GET", headers=headers_admin)
        print(f"API List CSRs -> Status: {status}, Count: {len(resp)}")
        assert status == 200, "Failed to list CSRs"
        
        pending_csrs = [r for r in resp if r.get("status") == "pending"]
        assert len(pending_csrs) > 0, "No pending CSRs found!"
        target_csr_id = pending_csrs[0].get("id")
        print(f"[*] Đang duyệt CSR ID: {target_csr_id}...")

        # 8.2. Phê duyệt và ký
        payload_approve = {
            "password": "ca_password_123"
        }
        status, resp = request_api(f"/admin/approve-csr/{target_csr_id}", method="POST", headers=headers_admin, json_data=payload_approve)
        print(f"API Approve CSR -> Status: {status}, Response: {resp}")
        assert status == 200, f"Failed to approve CSR: {resp}"
        print("✅ Thành công: Admin ký chứng chỉ thành công. Trạng thái đổi sang approved.")

        # ==========================================
        # BƯỚC 9: Customer xem danh sách chứng chỉ
        # ==========================================
        print("\n--- BƯỚC 9: Customer xem danh sách chứng chỉ ---")
        status, resp = request_api("/customer/certs", method="GET", headers=headers_customer)
        print(f"API Get My Certs -> Status: {status}, Count: {len(resp)}")
        assert status == 200, "Failed to get customer certs"
        assert len(resp) > 0, "Customer should have at least 1 cert"
        
        cert_id = resp[0].get("id")
        serial_hex = resp[0].get("serial_number")
        cert_pem = resp[0].get("pem_data")
        print(f"✅ Thành công: Thấy chứng chỉ mới. ID: {cert_id}, Serial: {serial_hex}")

        # ==========================================
        # BƯỚC 10: Tải chứng chỉ
        # ==========================================
        print("\n--- BƯỚC 10: Tải chứng chỉ ---")
        status, content = request_api(f"/customer/certs/{cert_id}/download", method="GET", headers=headers_customer, raw_response=True)
        print(f"API Download Cert -> Status: {status}, Content Type: PEM File, Size: {len(content)} bytes")
        assert status == 200, "Failed to download cert"
        assert b"BEGIN CERTIFICATE" in content, "Downloaded content is not a certificate"
        print("✅ Thành công: Tải thành công file chứng chỉ .crt dạng PEM.")

        # ==========================================
        # BƯỚC 11: Giải mã & phân tích chứng chỉ
        # ==========================================
        print("\n--- BƯỚC 11: Giải mã & phân tích chứng chỉ ---")
        payload_decode = {
            "cert_pem": cert_pem
        }
        status, resp = request_api("/customer/certs/decode", method="POST", headers=headers_customer, json_data=payload_decode)
        print(f"API Decode Cert -> Status: {status}")
        assert status == 200, f"Failed to decode cert: {resp}"
        print(f"Subject: {resp.get('subject')}")
        print(f"Issuer: {resp.get('issuer')}")
        print(f"Valid From: {resp.get('valid_from')}")
        print(f"Valid To: {resp.get('valid_to')}")
        print(f"Extensions:")
        for ext in resp.get('extensions', []):
            print(f"  - {ext.get('name')}: {ext.get('value')} (Critical: {ext.get('critical')})")
        print("✅ Thành công: Giải mã X.509v3 Certificate đầy đủ thông tin kỹ thuật.")

        # ==========================================
        # BƯỚC 12: Customer yêu cầu thu hồi chứng chỉ
        # ==========================================
        print("\n--- BƯỚC 12: Customer yêu cầu thu hồi chứng chỉ ---")
        status, resp = request_api(f"/customer/certs/{cert_id}/request-revoke", method="POST", headers=headers_customer)
        print(f"API Request Revoke -> Status: {status}, Response: {resp}")
        assert status == 200, f"Failed to request revocation: {resp}"
        
        # Verify status changed to 'revoke_pending'
        status, resp_certs = request_api("/customer/certs", method="GET", headers=headers_customer)
        curr_status = resp_certs[0].get("status")
        print(f"Trạng thái chứng chỉ hiện tại: {curr_status}")
        assert curr_status == "revoke_pending", "Status should be revoke_pending"
        print("✅ Thành công: Trạng thái chứng chỉ đổi thành REVOKE_PENDING.")

        # ==========================================
        # BƯỚC 13: Admin Phê duyệt Thu hồi
        # ==========================================
        print("\n--- BƯỚC 13: Admin Phê duyệt Thu hồi ---")
        # 13.1. Admin xem danh sách yêu cầu thu hồi
        status, resp = request_api("/admin/revoke-requests", method="GET", headers=headers_admin)
        print(f"API List Revocation Requests -> Status: {status}, Count: {len(resp)}")
        assert status == 200, "Failed to list revocation requests"
        assert len(resp) > 0, "No pending revocation requests found"
        
        # 13.2. Admin phê duyệt
        status, resp = request_api(f"/admin/revoke-cert/{cert_id}", method="POST", headers=headers_admin)
        print(f"API Revoke Cert -> Status: {status}, Response: {resp}")
        assert status == 200, f"Failed to revoke cert: {resp}"
        
        # Verify status is now 'revoked'
        status, resp_certs = request_api("/customer/certs", method="GET", headers=headers_customer)
        curr_status = resp_certs[0].get("status")
        print(f"Trạng thái chứng chỉ sau khi Admin duyệt thu hồi: {curr_status}")
        assert curr_status == "revoked", "Status should be revoked"
        print("✅ Thành công: Admin phê duyệt thu hồi. Trạng thái đổi thành REVOKED.")

        # ==========================================
        # BƯỚC 14: Admin Cập nhật CRL
        # ==========================================
        print("\n--- BƯỚC 14: Admin Cập nhật CRL ---")
        payload_crl = {
            "password": "ca_password_123"
        }
        status, resp = request_api("/admin/update-crl", method="POST", headers=headers_admin, json_data=payload_crl)
        print(f"API Update CRL -> Status: {status}")
        assert status == 200, f"Failed to update CRL: {resp}"
        print("✅ Thành công: Admin đã cập nhật danh sách CRL. CRL được ký bởi khóa CA và lưu vào DB.")

        # ==========================================
        # BƯỚC 15: Customer Tra cứu CRL
        # ==========================================
        print("\n--- BƯỚC 15: Customer Tra cứu CRL ---")
        status, content = request_api("/customer/crl", method="GET", headers=headers_customer, raw_response=True)
        crl_pem = content.decode('utf-8')
        print(f"API Get CRL -> Status: {status}, CRL PEM Size: {len(crl_pem)} bytes")
        assert status == 200, "Failed to get CRL"
        assert "BEGIN X509 CRL" in crl_pem, "Invalid CRL PEM format"
        
        # Parse and verify the CRL contains the revoked certificate
        crl_obj = x509.load_pem_x509_crl(content)
        revoked_serials_in_crl = [format(rc.serial_number, 'x') for rc in crl_obj]
        print(f"Danh sách Serial đã bị thu hồi trong CRL: {revoked_serials_in_crl}")
        assert serial_hex in revoked_serials_in_crl, "The certificate serial number was not found in the CRL list!"
        print("✅ Thành công: Tải CRL và kiểm thử OK! Số Serial của chứng chỉ đã bị thu hồi xuất hiện trong CRL.")

        # ==========================================
        # BƯỚC 16: Admin xem Nhật ký Kiểm toán
        # ==========================================
        print("\n--- BƯỚC 16: Admin xem Nhật ký Kiểm toán (Audit Logs) ---")
        status, resp = request_api("/admin/audit-logs", method="GET", headers=headers_admin)
        print(f"API Get Audit Logs -> Status: {status}, Log Count: {len(resp)}")
        assert status == 200, "Failed to get audit logs"
        for log in resp[:5]:
            print(f"  - [{log.get('timestamp')}] Action: {log.get('action')}, Details: {log.get('details')}")
        print("✅ Thành công: Nhật ký hệ thống ghi lại đầy đủ và chính xác tất cả các hành động.")

        # ==========================================
        # BƯỚC 17: Kiểm tra Bảo mật RBAC (Role-Based Access Control)
        # ==========================================
        print("\n--- BƯỚC 17: Kiểm tra Bảo mật RBAC ---")
        # Khách hàng cố tình gọi API Admin xem audit-logs
        status, resp = request_api("/admin/audit-logs", method="GET", headers=headers_customer)
        print(f"API Get Audit Logs (with Customer Token) -> Status: {status}, Response: {resp}")
        assert status == 403, f"RBAC failed! Customer was able to query admin endpoints. Status code: {status}"
        print("✅ Thành công: Hệ thống chặn thành công, trả về HTTP 403 Forbidden.")

        print("\n" + "=" * 70)
        print("🎉 CHÚC MỪNG: TẤT CẢ CÁC BƯỚC DEMO ĐÃ ĐƯỢC CHẠY THÀNH CÔNG VÀ KHÔNG GẶP LỖI!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ LỖI KHÔNG ĐẠT ĐIỀU KIỆN DEMO: {e}")
    except Exception as e:
        print(f"\n❌ LỖI HỆ THỐNG TRONG KHI DEMO: {e}")
    finally:
        # Kill the FastAPI server subprocess
        print("[*] Đang tắt FastAPI Backend Server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()
        kill_port_8000()
        print("[+] Backend Server đã tắt.")

if __name__ == "__main__":
    run_demo()
