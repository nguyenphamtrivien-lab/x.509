from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQL Server connection string (Using Windows Authentication)
# Note: "localhost" might need to be changed to "localhost\SQLEXPRESS" or your PC Name based on SSMS login
SERVER_NAME = "localhost" 
DATABASE_NAME = "PKI_X509"

# Connection string configuration using pyodbc
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("✅ SQL Server connection successfully initialized!")
except Exception as e:
    print(f"❌ Database connection error: {e}")

# Dependency to establish and close database sessions per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()