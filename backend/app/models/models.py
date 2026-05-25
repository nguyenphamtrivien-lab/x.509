"""
File: backend/app/models/models.py
Description: SQLAlchemy database models.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="customer") # "admin" or "customer"
    is_active = Column(Boolean, default=True)

    # Quan hệ
    certificates = relationship("Certificate", back_populates="user")
    cert_requests = relationship("CertRequest", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    serial_number = Column(String(255), unique=True, index=True, nullable=False)
    subject = Column(String(500), nullable=False)
    issuer = Column(String(500), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="active") # active, revoked, expired
    pem_data = Column(Text, nullable=False)

    user = relationship("User", back_populates="certificates")

class CertRequest(Base):
    __tablename__ = "cert_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    csr_data = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending") # pending, approved, rejected
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="cert_requests")

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(255), unique=True, nullable=False)
    config_value = Column(String(255), nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    details = Column(Text)

    user = relationship("User", back_populates="audit_logs")
