CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'customer',
    is_active BIT DEFAULT 1
);

CREATE TABLE certificates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    serial_number VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    issuer VARCHAR(500) NOT NULL,
    valid_from DATETIME NOT NULL,
    valid_to DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    pem_data TEXT NOT NULL,
    CONSTRAINT FK_Cert_User FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE cert_requests (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    csr_data TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Request_User FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE system_configs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value VARCHAR(255) NOT NULL
);

CREATE TABLE audit_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT GETDATE(),
    details TEXT,
    CONSTRAINT FK_Audit_User FOREIGN KEY (user_id) REFERENCES users(id)
);