-- ==================== AUDIT TABLES ====================
-- This schema creates 4 audit tables for comprehensive logging

-- 1. Performance Logs - System performance metrics
CREATE TABLE IF NOT EXISTS performance_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    server_type VARCHAR(50) NOT NULL,  -- SECURITY_SERVER, GLOBAL_SERVER
    server_id VARCHAR(100) NOT NULL,
    cpu_usage_percent FLOAT NOT NULL,
    memory_usage_percent FLOAT NOT NULL,
    total_memory_mb INT NOT NULL,
    used_memory_mb INT NOT NULL,
    disk_total_gb INT NOT NULL,
    disk_used_gb INT NOT NULL,
    disk_free_gb INT NOT NULL,
    active_connections INT NOT NULL,
    request_per_second FLOAT NOT NULL,
    status ENUM('NORMAL', 'WARNING', 'CRITICAL') DEFAULT 'NORMAL',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_server_id (server_id),
    INDEX idx_status (status),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2. Administration Logs - Administrative actions and changes
CREATE TABLE IF NOT EXISTS administration_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    server_type VARCHAR(50) NOT NULL,  -- SECURITY_SERVER, GLOBAL_SERVER
    server_id VARCHAR(100) NOT NULL,
    action_type VARCHAR(100) NOT NULL,  -- CREATE_ENTITY, UPDATE_NETWORK_CONFIG, DELETE_CERTIFICATE, etc.
    performed_by VARCHAR(255) NOT NULL,  -- Username or system identifier
    target_entity VARCHAR(255) NOT NULL,  -- Entity name or ID being modified
    previous_value LONGTEXT,  -- Previous state before change
    new_value LONGTEXT,  -- New state after change
    status ENUM('SUCCESS', 'FAILED') NOT NULL,
    error_message LONGTEXT,  -- Error details if FAILED
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_server_id (server_id),
    INDEX idx_action_type (action_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 3. Transactional Logs - Service request/response transactions
CREATE TABLE IF NOT EXISTS transactional_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    request_id VARCHAR(255) NOT NULL UNIQUE,  -- Unique request identifier
    client_subsystem VARCHAR(100) NOT NULL,
    provider_subsystem VARCHAR(100) NOT NULL,
    client_server_id VARCHAR(100) NOT NULL,
    provider_server_id VARCHAR(100) NOT NULL,
    service_code VARCHAR(100) NOT NULL,
    service_version VARCHAR(50) NOT NULL,
    request_time TIMESTAMP NOT NULL,  -- When request was received
    response_time TIMESTAMP NOT NULL,  -- When response was sent
    duration_ms INT NOT NULL,  -- Request processing duration
    response_status ENUM('SUCCESS', 'FAILED', 'TIMEOUT') NOT NULL,
    http_status_code INT NOT NULL,
    request_size_bytes INT NOT NULL,
    response_size_bytes INT NOT NULL,
    correlation_id VARCHAR(255) NOT NULL,  -- Correlation ID for request tracing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_request_id (request_id),
    INDEX idx_client_server_id (client_server_id),
    INDEX idx_provider_server_id (provider_server_id),
    INDEX idx_response_status (response_status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 4. Security Logs - Security events and access logs
CREATE TABLE IF NOT EXISTS security_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    server_type VARCHAR(50) NOT NULL,  -- SECURITY_SERVER, GLOBAL_SERVER
    server_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,  -- AUTH_SUCCESS, CERT_CREATED, ACCESS_GRANTED, PERMISSION_CHECK_FAILED, etc.
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL,
    user_id VARCHAR(255),
    subsystem VARCHAR(100),
    resource VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    status ENUM('SUCCESS', 'FAILED') NOT NULL,
    failure_reason LONGTEXT,
    ip_address VARCHAR(45) NOT NULL,
    geo_location VARCHAR(255),
    certificate_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_server_id (server_id),
    INDEX idx_event_type (event_type),
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_certificate_id (certificate_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ==================== VIEWS FOR AUDIT REPORTS ====================

-- Performance Summary View
CREATE OR REPLACE VIEW v_performance_summary AS
SELECT 
    server_id,
    MAX(recorded_at) as last_recorded,
    AVG(cpu_usage_percent) as avg_cpu,
    MAX(cpu_usage_percent) as peak_cpu,
    AVG(memory_usage_percent) as avg_memory,
    MAX(memory_usage_percent) as peak_memory,
    AVG(active_connections) as avg_connections,
    MAX(active_connections) as peak_connections,
    COUNT(*) as total_records
FROM performance_logs
WHERE recorded_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY server_id;


-- Security Events Summary View
CREATE OR REPLACE VIEW v_security_summary AS
SELECT 
    event_type,
    severity,
    COUNT(*) as event_count,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_count,
    MAX(created_at) as latest_event
FROM security_logs
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY event_type, severity;


-- Administration Actions Summary View
CREATE OR REPLACE VIEW v_administration_summary AS
SELECT 
    action_type,
    COUNT(*) as total_actions,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
    MAX(created_at) as last_action
FROM administration_logs
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY action_type;


-- Transaction Performance View
CREATE OR REPLACE VIEW v_transaction_performance AS
SELECT 
    service_code,
    COUNT(*) as total_requests,
    AVG(duration_ms) as avg_duration,
    MAX(duration_ms) as max_duration,
    MIN(duration_ms) as min_duration,
    SUM(CASE WHEN response_status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN response_status = 'FAILED' THEN 1 ELSE 0 END) as failed,
    SUM(CASE WHEN response_status = 'TIMEOUT' THEN 1 ELSE 0 END) as timeouts
FROM transactional_logs
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY service_code;
