from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

# Declarative base for SQLAlchemy models
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='customer')
    is_active = Column(Boolean, default=True)

    # Relationships for ORM querying
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    requests = relationship("CertRequest", back_populates="user", cascade="all, delete-orphan")


class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    serial_number = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    issuer = Column(String(500), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default='Active')
    pem_data = Column(Text, nullable=False)

    user = relationship("User", back_populates="certificates")


class CertRequest(Base):
    __tablename__ = 'cert_requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    csr_data = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default='Pending')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="requests")


class SystemConfig(Base):
    __tablename__ = 'system_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(255), unique=True, nullable=False)
    config_value = Column(String(255), nullable=False)


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(Text, nullable=True)