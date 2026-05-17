from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Chuỗi kết nối SQL Server (Sử dụng Windows Authentication)
# Lưu ý: Chữ "localhost" có thể cần đổi thành "localhost\SQLEXPRESS" hoặc "Tên_Máy_Tính" tùy vào lúc đăng nhập SSMS
SERVER_NAME = "localhost" 
DATABASE_NAME = "PKI_X509"

# Cấu hình chuỗi kết nối dùng pyodbc
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("✅ Đã khởi tạo kết nối SQL Server thành công!")
except Exception as e:
    print(f"❌ Lỗi kết nối DB: {e}")

# Hàm này dùng để mở kết nối mỗi khi có request gọi tới API, và đóng lại khi xong
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()