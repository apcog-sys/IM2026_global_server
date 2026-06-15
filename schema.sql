-- =========================
-- DATABASE
-- =========================
CREATE DATABASE IF NOT EXISTS gs1;
USE gs1;

-- =========================
-- 1. ENTITIES (ORGANIZATIONS)
-- =========================
CREATE TABLE IF NOT EXISTS entities (
    entity_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_code VARCHAR(50) UNIQUE NOT NULL,
    entity_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50),
    status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
    request_status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- 2. NETWORK CONFIG (SECURITY SERVER)
-- =========================
CREATE TABLE IF NOT EXISTS network_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    version VARCHAR(50),
    network_instance VARCHAR(50),

    gateway_code VARCHAR(100) UNIQUE NOT NULL,
    entity_id INT NOT NULL,

    host VARCHAR(255),
    port INT,
    hostname VARCHAR(255),
    ip_address VARCHAR(50),
    environment VARCHAR(50),

    status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',

    auth_cert_id INT NULL,
    sign_cert_id INT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (entity_id) REFERENCES entities(entity_id),
    UNIQUE KEY unique_gateway (gateway_code)
);

-- =========================
-- 3. SERVER KEYS
-- =========================
CREATE TABLE IF NOT EXISTS server_keys (
    key_id INT AUTO_INCREMENT PRIMARY KEY,
    gateway_code VARCHAR(100),
    key_type ENUM('AUTH','SIGN'),
    public_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code),
    UNIQUE KEY unique_key (gateway_code, key_type)
);

-- =========================
-- 4. CSR REQUESTS
-- =========================
CREATE TABLE IF NOT EXISTS certificate_requests (
    csr_id INT AUTO_INCREMENT PRIMARY KEY,
    gateway_code VARCHAR(100),
    key_id INT,
    csr_data TEXT,

    cert_type ENUM('AUTH','SIGN'),
    status ENUM('PENDING','SIGNED','REJECTED') DEFAULT 'PENDING',

    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (key_id) REFERENCES server_keys(key_id),
    FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
);

-- =========================
-- 5. CERTIFICATES
-- =========================
CREATE TABLE IF NOT EXISTS certificates (
    cert_id INT AUTO_INCREMENT PRIMARY KEY,
    gateway_code VARCHAR(100),
    key_id INT,

    cert_type ENUM('AUTH','SIGN'),
    certificate TEXT,

    issued_by VARCHAR(255),
    valid_from DATETIME,
    valid_to DATETIME,

    status ENUM('ACTIVE','EXPIRED','REVOKED') DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (key_id) REFERENCES server_keys(key_id),
    FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
);

-- =========================
-- 6. REGISTRATION LOG
-- =========================
CREATE TABLE IF NOT EXISTS registration_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    gateway_code VARCHAR(100),

    action ENUM('SUBMITTED','APPROVED','REJECTED'),
    performed_by VARCHAR(100),
    remarks TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
);

-- =========================
-- 7. SUBSYSTEMS (APPLICATIONS)
-- =========================
CREATE TABLE IF NOT EXISTS subsystems (
    subsystem_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id INT NOT NULL,
    subsystem_code VARCHAR(100) NOT NULL,
    subsystem_name VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
    UNIQUE KEY unique_subsystem_code (subsystem_code)
);

-- =========================
-- 8. GLOBAL SERVICE REGISTER
-- =========================
CREATE TABLE IF NOT EXISTS global_service_register (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id INT NOT NULL,
    subsystem_id INT NOT NULL,
    service_code VARCHAR(100) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    service_version VARCHAR(50),
    full_service_id VARCHAR(255),
    service_url VARCHAR(500),
    http_method VARCHAR(20),
    protocol VARCHAR(20),
    security_server_id INT,
    description TEXT,
    status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
    FOREIGN KEY (subsystem_id) REFERENCES subsystems(subsystem_id) ON DELETE CASCADE,
    FOREIGN KEY (security_server_id) REFERENCES network_config(id) ON DELETE SET NULL,
    UNIQUE KEY unique_service_code (service_code)
);

-- =========================
-- 9. GLOBAL DIRECTORY
-- =========================
CREATE TABLE IF NOT EXISTS global_directory (
    directory_id INT AUTO_INCREMENT PRIMARY KEY,

    entity_code VARCHAR(50),
    gateway_code VARCHAR(100),

    service_url VARCHAR(255),

    auth_cert_id INT,
    sign_cert_id INT,

    status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (auth_cert_id) REFERENCES certificates(cert_id),
    FOREIGN KEY (sign_cert_id) REFERENCES certificates(cert_id),
    UNIQUE KEY unique_gateway_entry (gateway_code)
);

-- Create indexes
CREATE INDEX idx_gateway_code ON network_config(gateway_code);
CREATE INDEX idx_entity_code ON entities(entity_code);
CREATE INDEX idx_cert_gateway ON certificates(gateway_code);
CREATE INDEX idx_log_gateway ON registration_log(gateway_code);
