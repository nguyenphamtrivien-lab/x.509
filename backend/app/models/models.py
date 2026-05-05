"""
File: backend/app/models/models.py
Description: SQLAlchemy database models.
TODO:
- Add relationship between models (e.g., User -> Certificate, User -> CertRequest).
- Add specific data types and constraints (e.g., String lengths).
- Define base class.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()
# class User(Base):

class User:
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password_hash = Column(String)
    role = Column(String) # admin or customer
    is_active = Column(Boolean)

class Certificate:
    id = Column(Integer, primary_key=True)
    serial_number = Column(String)
    subject = Column(String)
    issuer = Column(String)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    status = Column(String) # active, revoked, expired
    pem_data = Column(Text)

class CertRequest:
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    csr_data = Column(Text)
    status = Column(String) # pending, approved, rejected
    created_at = Column(DateTime)

class SystemConfig:
    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)

class AuditLog:
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String)
    timestamp = Column(DateTime)
    details = Column(Text)
