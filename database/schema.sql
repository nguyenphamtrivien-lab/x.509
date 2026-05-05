-- File: database/schema.sql
-- Description: MySQL database schema definition for the X.509 system.
-- TODO:
-- - Add foreign key constraints.
-- - Add indexes for performance.
-- - Refine data types and lengths.

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    serial_number VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    issuer VARCHAR(500) NOT NULL,
    valid_from DATETIME NOT NULL,
    valid_to DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL,
    pem_data TEXT NOT NULL
);

CREATE TABLE cert_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    csr_data TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE system_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL,
    config_value VARCHAR(255) NOT NULL
);

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    details TEXT
);
