from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import mysql.connector
from mysql.connector import Error

from datetime import datetime
import uvicorn
import os
import json
import requests

# ==================== Pydantic Models ====================

class DBConfig(BaseModel):
    host: str
    port: int = 3306
    username: str
    password: str
    database: str


# 1. ENTITIES Models
class Entity(BaseModel):
    entity_code: str
    entity_name: str
    entity_type: str
    status: str = "ACTIVE"
    request_status: str = "PENDING"

class EntityResponse(Entity):
    entity_id: int
    created_at: Optional[str] = None


# 2. NETWORK_CONFIG Models
class NetworkConfig(BaseModel):
    title: str
    version: str
    network_instance: str
    gateway_code: str
    entity_id: int
    host: str
    port: int
    hostname: str
    ip_address: str
    environment: str
    status: str = "INACTIVE"

class NetworkConfigUpdate(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None
    network_instance: Optional[str] = None
    gateway_code: Optional[str] = None
    entity_id: Optional[int] = None
    host: Optional[str] = None
    port: Optional[int] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[str] = None


# 3. SERVER_KEYS Models
class ServerKey(BaseModel):
    gateway_code: str
    key_type: str  # AUTH or SIGN
    public_key: str

class ServerKeyUpdate(BaseModel):
    public_key: Optional[str] = None


# 4. CERTIFICATE_REQUESTS Models
class CertificateRequest(BaseModel):
    gateway_code: str
    key_id: int
    csr_data: str
    cert_type: str  # AUTH or SIGN

class CertificateRequestUpdate(BaseModel):
    status: Optional[str] = None


# 5. CERTIFICATES Models
class Certificate(BaseModel):
    gateway_code: str
    key_id: int
    cert_type: str  # AUTH or SIGN
    certificate: str
    issued_by: str
    valid_from: str
    valid_to: str

class CertificateUpdate(BaseModel):
    status: Optional[str] = None

class SaveSignedCertificateRequest(BaseModel):
    csr_id: int
    ca_response: dict  # Contains: certificate_pem, issued_date, expiry_date, certificate_id


# 6. REGISTRATION_LOG Models
class RegistrationLog(BaseModel):
    gateway_code: str
    action: str  # SUBMITTED, APPROVED, REJECTED
    performed_by: str
    remarks: Optional[str] = None

class RegistrationLogUpdate(BaseModel):
    action: Optional[str] = None
    performed_by: Optional[str] = None
    remarks: Optional[str] = None


# 7. GLOBAL_DIRECTORY Models
class GlobalDirectoryEntry(BaseModel):
    entity_code: str
    gateway_code: str
    service_url: str
    auth_cert_id: int
    sign_cert_id: int

class GlobalDirectoryUpdate(BaseModel):
    service_url: Optional[str] = None
    status: Optional[str] = None


# 8. SUBSYSTEMS Models
class Subsystem(BaseModel):
    entity_id: int
    subsystem_code: str
    subsystem_name: str
    description: Optional[str] = None
    status: str = "ACTIVE"

class SubsystemUpdate(BaseModel):
    entity_id: Optional[int] = None
    subsystem_code: Optional[str] = None
    subsystem_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


# 9. GLOBAL_SERVICE_REGISTER Models
class GlobalServiceRegister(BaseModel):
    entity_id: int
    subsystem_id: int
    service_code: str
    service_name: str
    service_version: str
    full_service_id: str
    service_url: str
    http_method: str
    protocol: str
    security_server_id: int
    description: Optional[str] = None
    status: str = "ACTIVE"

class GlobalServiceRegisterUpdate(BaseModel):
    entity_id: Optional[int] = None
    subsystem_id: Optional[int] = None
    service_code: Optional[str] = None
    service_name: Optional[str] = None
    service_version: Optional[str] = None
    full_service_id: Optional[str] = None
    service_url: Optional[str] = None
    http_method: Optional[str] = None
    protocol: Optional[str] = None
    security_server_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None


# 10. UNIFIED SECURITY SERVER REGISTRATION Model
class SecurityServerRegistration(BaseModel):
    """Unified model for registering security server with CSR certificates
    
    Required parameters:
    - gateway_code: Unique identifier for the security server
    - title: Name/title of the security server
    - version: Version of the security server configuration
    - network_instance: Network instance identifier
    - entity_name: Name of the entity owning this server
    - host: Hostname or IP for connections
    - port: Port number for connections
    - hostname: Hostname for the server
    - ip_address: IP address of the server
    - environment: Environment (production, staging, etc.)
    - auth_csr_content: CSR data for AUTH certificate
    - sign_csr_content: CSR data for SIGN certificate
    """
    gateway_code: str
    title: str
    version: str
    network_instance: str
    entity_name: str
    host: str
    port: int
    hostname: str
    ip_address: str
    environment: str
    auth_csr_content: str  # CSR data for AUTH certificate
    sign_csr_content: str  # CSR data for SIGN certificate


# 11. AUDIT MODELS - Performance Logs
class PerformanceLog(BaseModel):
    """Performance monitoring metrics - server_type: SECURITY_SERVER or GLOBAL_SERVER"""
    server_type: str  # SECURITY_SERVER or GLOBAL_SERVER
    server_id: str
    cpu_usage_percent: float
    memory_usage_percent: float
    total_memory_mb: int
    used_memory_mb: int
    disk_total_gb: int
    disk_used_gb: int
    disk_free_gb: int
    active_connections: int
    request_per_second: float
    status: str = "NORMAL"  # NORMAL, WARNING, CRITICAL


# 12. AUDIT MODELS - Administration Logs
class AdministrationLog(BaseModel):
    """Administrative action logging"""
    server_type: str  # SECURITY_SERVER or GLOBAL_SERVER
    server_id: str
    action_type: str  # CREATE_ENTITY, UPDATE_NETWORK_CONFIG, DELETE_CERTIFICATE, etc.
    performed_by: str
    target_entity: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    status: str  # SUCCESS or FAILED
    error_message: Optional[str] = None
    ip_address: str
    user_agent: str


# 13. AUDIT MODELS - Transactional Logs
class TransactionalLog(BaseModel):
    """Service request/response transaction logging"""
    request_id: str
    client_subsystem: str
    provider_subsystem: str
    client_server_id: str
    provider_server_id: str
    service_code: str
    service_version: str
    request_time: datetime  # When request was received
    response_time: datetime  # When response was sent
    duration_ms: int
    response_status: str  # SUCCESS, FAILED, TIMEOUT
    http_status_code: int
    request_size_bytes: int
    response_size_bytes: int
    correlation_id: str


# 14. AUDIT MODELS - Security Logs
class SecurityLog(BaseModel):
    """Security event logging"""
    server_type: str  # SECURITY_SERVER or GLOBAL_SERVER
    server_id: str
    event_type: str  # AUTH_SUCCESS, CERT_CREATED, ACCESS_GRANTED, PERMISSION_CHECK_FAILED, etc.
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    user_id: Optional[str] = None
    subsystem: Optional[str] = None
    resource: str
    action: str
    status: str  # SUCCESS or FAILED
    failure_reason: Optional[str] = None
    ip_address: str
    geo_location: Optional[str] = None
    certificate_id: Optional[str] = None


# ==================== FastAPI App Setup ====================

app = FastAPI(
    title="Global Server - Security Registration System",
    description="REST API for managing security server registration with progressive trust model",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global database configuration
db_config: Optional[DBConfig] = None


# ==================== Load Configuration from config.json ====================

def load_config_from_file():
    """Load database configuration from config.json"""
    global db_config
    config_file = "config.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                db_info = config_data.get("database", {})
                
                db_config = DBConfig(
                    host=db_info.get("host", "localhost"),
                    port=db_info.get("port", 3306),
                    username=db_info.get("username", "root"),
                    password=db_info.get("password", "root"),
                    database=db_info.get("database", "gs1")
                )
                print(f"✓ Database config loaded: {db_config.host}:{db_config.port}/{db_config.database}")
                
        except Exception as e:
            print(f"✗ Error loading config.json: {str(e)}")
    else:
        print(f"⚠ config.json not found. Database configuration required.")




# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Load config on server startup"""
    load_config_from_file()
    print("✓ Server started. Connected to database.")


# ==================== Database Manager ====================

class DatabaseManager:
    @staticmethod
    def get_connection():
        global db_config
        if not db_config:
            raise HTTPException(status_code=400, detail="Database configuration not set")
        try:
            connection = mysql.connector.connect(
                host=db_config.host,
                port=db_config.port,
                user=db_config.username,
                password=db_config.password,
                database=db_config.database
            )
            return connection
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

    @staticmethod
    def test_connection(config: DBConfig):
        try:
            connection = mysql.connector.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database
            )
            connection.close()
            return True
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


# ==================== Helper Functions ====================

def normalize_pem_format(pem_data: str) -> str:
    """
    Normalize PEM data by ensuring proper line breaks.
    Handles both literal \n characters and actual newlines.
    """
    if not pem_data:
        return pem_data
    
    # Replace literal \n with actual newlines (for double-escaped strings)
    pem_data = pem_data.replace('\\n', '\n')
    
    # Ensure the PEM starts and ends with proper markers
    pem_data = pem_data.strip()
    
    return pem_data


# ==================== AUDIT LOGGING HELPER FUNCTIONS ====================

def log_administration_action(
    action_type: str,
    performed_by: str,
    target_entity: str,
    status: str,
    previous_value: Optional[str] = None,
    new_value: Optional[str] = None,
    error_message: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """Log administrative actions to administration_logs table"""
    if not db_config:
        return
    
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO administration_logs 
        (server_type, server_id, action_type, performed_by, target_entity, 
         previous_value, new_value, status, error_message, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            'GLOBAL_SERVER', 'GLOBAL_SERVER_01', action_type, performed_by, target_entity,
            previous_value, new_value, status, error_message, ip_address or '0.0.0.0'
        ))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to log admin action: {str(e)}")


def log_security_event(
    event_type: str,
    severity: str,
    resource: str,
    action: str,
    status: str,
    user_id: Optional[str] = None,
    subsystem: Optional[str] = None,
    failure_reason: Optional[str] = None,
    ip_address: Optional[str] = None,
    certificate_id: Optional[str] = None
):
    """Log security events to security_logs table"""
    if not db_config:
        return
    
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO security_logs 
        (server_type, server_id, event_type, severity, resource, action, status,
         user_id, subsystem, failure_reason, ip_address, certificate_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            'GLOBAL_SERVER', 'GLOBAL_SERVER_01', event_type, severity, resource, action, status,
            user_id, subsystem, failure_reason, ip_address or '0.0.0.0', certificate_id
        ))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to log security event: {str(e)}")


def log_transaction(
    request_id: str,
    client_subsystem: str,
    provider_subsystem: str,
    service_code: str,
    response_status: str,
    duration_ms: int,
    http_status_code: Optional[int] = None,
    client_server_id: Optional[str] = None,
    provider_server_id: Optional[str] = None
):
    """Log transactional data to transactional_logs table"""
    if not db_config:
        return
    
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO transactional_logs 
        (request_id, client_subsystem, provider_subsystem, service_code, 
         response_status, duration_ms, http_status_code, client_server_id, provider_server_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            request_id, client_subsystem, provider_subsystem, service_code,
            response_status, duration_ms, http_status_code, client_server_id, provider_server_id
        ))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to log transaction: {str(e)}")


# ==================== Frontend Routes ====================

@app.get("/")
async def root():
    """Serve the main HTML frontend"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, "index.html")
    if os.path.exists(html_file):
        # Disable caching so frontend edits are always reflected on reload
        no_cache_headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return FileResponse(html_file, media_type="text/html", headers=no_cache_headers)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


# ==================== Database Configuration Endpoints ====================

@app.post("/api/save-db-config")
async def save_db_config(config: DBConfig):
    global db_config
    try:
        DatabaseManager.test_connection(config)
        db_config = config
        return {
            "status": "success",
            "message": "Database configuration saved",
            "config": {
                "host": config.host,
                "port": config.port,
                "username": config.username,
                "database": config.database
            }
        }
    except HTTPException as e:
        raise e


@app.post("/api/test-connection")
async def test_connection(config: DBConfig):
    try:
        DatabaseManager.test_connection(config)
        return {"status": "success", "message": "Connection successful"}
    except HTTPException as e:
        raise e


# ==================== TABLE 1: ENTITIES CRUD ====================

@app.post("/api/entities")
async def create_entity(entity: Entity):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO entities (entity_code, entity_name, entity_type, status, request_status)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (entity.entity_code, entity.entity_name, entity.entity_type, entity.status, entity.request_status))
        connection.commit()
        entity_id = cursor.lastrowid
        
        # Log the creation action
        log_administration_action(
            action_type="CREATE_ENTITY",
            performed_by="SYSTEM",
            target_entity=f"Entity: {entity.entity_name}",
            status="SUCCESS",
            new_value=f"entity_code={entity.entity_code}, entity_type={entity.entity_type}"
        )
        
        # Log security event for entity creation
        log_security_event(
            event_type="ENTITY_CREATED",
            severity="MEDIUM",
            resource=f"ENTITY:{entity.entity_code}",
            action="CREATE",
            status="SUCCESS",
            user_id="SYSTEM",
            subsystem="ENTITY_MANAGEMENT"
        )
        
        return {"status": "success", "message": "Entity created", "entity_id": entity_id}
    except Error as e:
        if connection:
            connection.rollback()
        # Log the error
        log_administration_action(
            action_type="CREATE_ENTITY",
            performed_by="SYSTEM",
            target_entity=f"Entity: {entity.entity_name}",
            status="FAILED",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/entities")
async def get_all_entities():
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM entities ORDER BY created_at DESC")
        entities = cursor.fetchall()
        
        for entity in entities:
            if entity.get('created_at'):
                entity['created_at'] = entity['created_at'].isoformat()
        
        return {"status": "success", "total": len(entities), "entities": entities}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/entities/{entity_id}")
async def get_entity(entity_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM entities WHERE entity_id = %s", (entity_id,))
        entity = cursor.fetchone()
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        if entity.get('created_at'):
            entity['created_at'] = entity['created_at'].isoformat()
        
        return {"status": "success", "entity": entity}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/entities/code/{entity_code}")
async def get_entity_by_code(entity_code: str):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM entities WHERE entity_code = %s", (entity_code,))
        entity = cursor.fetchone()
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        if entity.get('created_at'):
            entity['created_at'] = entity['created_at'].isoformat()
        
        return {"status": "success", "entity": entity}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/entities/status/{status}")
async def get_entities_by_status(status: str):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM entities WHERE status = %s ORDER BY created_at DESC", (status.upper(),))
        entities = cursor.fetchall()
        
        for entity in entities:
            if entity.get('created_at'):
                entity['created_at'] = entity['created_at'].isoformat()
        
        return {"status": "success", "total": len(entities), "filter_status": status.upper(), "entities": entities}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/entities/{entity_id}")
async def update_entity(entity_id: int, entity_update: Entity):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        UPDATE entities 
        SET entity_code=%s, entity_name=%s, entity_type=%s, status=%s, request_status=%s
        WHERE entity_id=%s
        """
        cursor.execute(query, (
            entity_update.entity_code,
            entity_update.entity_name,
            entity_update.entity_type,
            entity_update.status,
            entity_update.request_status,
            entity_id
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        connection.commit()
        return {"status": "success", "message": "Entity updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/entities/{entity_id}")
async def delete_entity(entity_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM entities WHERE entity_id = %s", (entity_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        connection.commit()
        return {"status": "success", "message": "Entity deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/entities/{entity_id}/request-status")
async def update_entity_request_status(entity_id: int, request_body: dict):
    """Update entity request status (PENDING, APPROVED, REJECTED)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    request_status = request_body.get("request_status", "").upper()
    if request_status not in ["PENDING", "APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid request_status. Must be PENDING, APPROVED, or REJECTED")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Check if entity exists
        check_query = "SELECT entity_id, request_status FROM entities WHERE entity_id = %s"
        cursor.execute(check_query, (entity_id,))
        entity = cursor.fetchone()
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Update request status
        update_query = "UPDATE entities SET request_status = %s WHERE entity_id = %s"
        cursor.execute(update_query, (request_status, entity_id))
        connection.commit()
        
        return {
            "status": "success",
            "message": f"Entity request status updated to {request_status}",
            "entity_id": entity_id,
            "request_status": request_status
        }
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== UNIFIED SECURITY SERVER REGISTRATION ====================

@app.post("/api/register-security-server")
async def register_security_server(registration: SecurityServerRegistration):
    """
    Register a security server with CSR certificates.
    Flow:
    1. Verify entity exists
    2. Create network config for the security server (status: INACTIVE)
    3. Create CSR certificate requests for both AUTH and SIGN (status: PENDING)
    4. Log the registration submission
    Returns: network_config_id and CSR IDs for admin to process
    """
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Step 1: Verify entity exists by name and get its ID
        check_entity_query = "SELECT entity_id FROM entities WHERE entity_name = %s"
        cursor.execute(check_entity_query, (registration.entity_name,))
        entity_record = cursor.fetchone()
        if not entity_record:
            raise HTTPException(
                status_code=400,
                detail=f"Entity '{registration.entity_name}' does not exist. Please create entity first."
            )
        entity_id = entity_record[0]
        
        # Step 2: Create network config with INACTIVE status
        network_config_query = """
        INSERT INTO network_config 
        (gateway_code, entity_id, title, version, network_instance, host, port, hostname, ip_address, environment, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'INACTIVE')
        """
        cursor.execute(network_config_query, (
            registration.gateway_code,
            entity_id,
            registration.title,
            registration.version,
            registration.network_instance,
            registration.host,
            registration.port,
            registration.hostname,
            registration.ip_address,
            registration.environment
        ))
        network_config_id = cursor.lastrowid
        connection.commit()
        
        # Step 3: Create AUTH CSR certificate request with PENDING status
        auth_csr_query = """
        INSERT INTO certificate_requests (gateway_code, key_id, csr_data, cert_type, status)
        VALUES (%s, %s, %s, %s, 'PENDING')
        """
        cursor.execute(auth_csr_query, (
            registration.gateway_code,
            None,  # No key_id yet
            registration.auth_csr_content,
            'AUTH'
        ))
        auth_csr_id = cursor.lastrowid
        connection.commit()
        
        # Step 4: Create SIGN CSR certificate request with PENDING status
        sign_csr_query = """
        INSERT INTO certificate_requests (gateway_code, key_id, csr_data, cert_type, status)
        VALUES (%s, %s, %s, %s, 'PENDING')
        """
        cursor.execute(sign_csr_query, (
            registration.gateway_code,
            None,  # No key_id yet
            registration.sign_csr_content,
            'SIGN'
        ))
        sign_csr_id = cursor.lastrowid
        connection.commit()
        
        # Step 5: Log the registration submission
        log_query = """
        INSERT INTO registration_log (gateway_code, action, performed_by)
        VALUES (%s, 'SUBMITTED', 'security_server')
        """
        cursor.execute(log_query, (registration.gateway_code,))
        connection.commit()
        
        # Log administration action
        log_administration_action(
            action_type="CREATE_SECURITY_SERVER",
            performed_by="SYSTEM",
            target_entity=f"Gateway: {registration.gateway_code}",
            status="SUCCESS",
            new_value=f"title={registration.title}, entity={registration.entity_name}, status=INACTIVE"
        )
        
        # Log security event
        log_security_event(
            event_type="SECURITY_SERVER_CREATED",
            severity="MEDIUM",
            resource=f"GATEWAY:{registration.gateway_code}",
            action="CREATE",
            status="SUCCESS",
            user_id="SYSTEM",
            subsystem="SECURITY_SERVER_MANAGEMENT"
        )
        
        return {
            "status": "success",
            "message": "Security server registered successfully. Awaiting CSR review.",
            "gateway_code": registration.gateway_code,
            "title": registration.title,
            "network_config_id": network_config_id,
            "network_config_status": "INACTIVE",
            "auth": {
                "csr_id": auth_csr_id,
                "status": "PENDING",
                "next_step": "Admin must generate certificate from CSR_REGISTRATION_MANAGEMENT tab"
            },
            "sign": {
                "csr_id": sign_csr_id,
                "status": "PENDING",
                "next_step": "Admin must generate certificate from CSR_REGISTRATION_MANAGEMENT tab"
            }
        }
    
    except HTTPException:
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise
    except Error as e:
        if connection:
            try:
                connection.rollback()
            except:
                pass
        # Log the error
        log_administration_action(
            action_type="CREATE_SECURITY_SERVER",
            performed_by="SYSTEM",
            target_entity=f"Gateway: {registration.gateway_code}",
            status="FAILED",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        if connection:
            try:
                connection.rollback()
            except:
                pass
        # Log the error
        log_administration_action(
            action_type="CREATE_SECURITY_SERVER",
            performed_by="SYSTEM",
            target_entity=f"Gateway: {registration.gateway_code}",
            status="FAILED",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if connection and connection.is_connected():
            try:
                connection.close()
            except:
                pass


# ==================== TABLE 2: NETWORK_CONFIG CRUD ====================

@app.post("/api/network-config")
async def create_network_config(config: NetworkConfig):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    cursor = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Check if entity_id exists
        check_query = "SELECT entity_id FROM entities WHERE entity_id = %s"
        cursor.execute(check_query, (config.entity_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"Entity ID {config.entity_id} does not exist")
        
        query = """
        INSERT INTO network_config 
        (gateway_code, entity_id, title, version, network_instance, host, port, hostname, ip_address, environment, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            config.gateway_code, config.entity_id, config.title, config.version,
            config.network_instance, config.host, config.port, config.hostname,
            config.ip_address, config.environment, "INACTIVE"
        ))
        connection.commit()
        
        # Auto-log SUBMITTED event (optional - skip if log table fails)
        try:
            log_query = """
            INSERT INTO registration_log (gateway_code, action, performed_by)
            VALUES (%s, 'SUBMITTED', 'security_server')
            """
            cursor.execute(log_query, (config.gateway_code,))
            connection.commit()
        except Exception as log_err:
            print(f"Warning: Failed to log registration: {log_err}")
            # Don't fail the registration if logging fails
        
        return {"status": "success", "message": "Gateway registered", "id": cursor.lastrowid}
    except HTTPException:
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise
    except Error as e:
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if connection and connection.is_connected():
            try:
                connection.close()
            except:
                pass


@app.get("/api/network-config")
async def get_all_network_configs():
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM network_config ORDER BY created_at DESC")
        configs = cursor.fetchall()
        
        for config in configs:
            if config.get('created_at'):
                config['created_at'] = config['created_at'].isoformat()
            if config.get('updated_at'):
                config['updated_at'] = config['updated_at'].isoformat()
        
        return configs
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/network-config/{gateway_code}")
async def get_network_config(gateway_code: str):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM network_config WHERE gateway_code = %s", (gateway_code,))
        config = cursor.fetchone()
        
        if not config:
            raise HTTPException(status_code=404, detail="Gateway not found")
        
        if config.get('created_at'):
            config['created_at'] = config['created_at'].isoformat()
        
        return {"status": "success", "config": config}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/network-config/{gateway_code}")
async def update_network_config(gateway_code: str, config_update: NetworkConfigUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        update_fields = []
        values = []
        
        for field, value in config_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = %s")
            values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(gateway_code)
        query = f"UPDATE network_config SET {', '.join(update_fields)} WHERE gateway_code = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Gateway not found")
        
        connection.commit()
        return {"status": "success", "message": "Gateway updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/network-config/{gateway_code}")
async def delete_network_config(gateway_code: str):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM network_config WHERE gateway_code = %s", (gateway_code,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Gateway not found")
        
        connection.commit()
        return {"status": "success", "message": "Gateway deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 3: SERVER_KEYS CRUD ====================

@app.post("/api/server-keys")
async def create_server_key(key: ServerKey):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO server_keys (gateway_code, key_type, public_key)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (key.gateway_code, key.key_type, key.public_key))
        connection.commit()
        
        return {"status": "success", "message": f"{key.key_type} key uploaded", "key_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/server-keys")
async def get_all_server_keys():
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM server_keys ORDER BY created_at DESC")
        keys = cursor.fetchall()
        
        for key in keys:
            if key.get('created_at'):
                key['created_at'] = key['created_at'].isoformat()
        
        return {"status": "success", "total": len(keys), "keys": keys}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/server-keys/{key_id}")
async def get_server_key(key_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM server_keys WHERE key_id = %s", (key_id,))
        key = cursor.fetchone()
        
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        if key.get('created_at'):
            key['created_at'] = key['created_at'].isoformat()
        
        return {"status": "success", "key": key}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/server-keys/gateway/{gateway_code}")
async def get_server_keys_by_gateway(gateway_code: str):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM server_keys WHERE gateway_code = %s ORDER BY created_at", (gateway_code,))
        keys = cursor.fetchall()
        
        for key in keys:
            if key.get('created_at'):
                key['created_at'] = key['created_at'].isoformat()
        
        return {"status": "success", "gateway_code": gateway_code, "total": len(keys), "keys": keys}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/server-keys/{key_id}")
async def update_server_key(key_id: int, key_update: ServerKeyUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        if key_update.public_key:
            cursor.execute(
                "UPDATE server_keys SET public_key = %s WHERE key_id = %s",
                (key_update.public_key, key_id)
            )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        
        connection.commit()
        return {"status": "success", "message": "Key updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/server-keys/{key_id}")
async def delete_server_key(key_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM server_keys WHERE key_id = %s", (key_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        
        connection.commit()
        return {"status": "success", "message": "Key deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 4: CERTIFICATE_REQUESTS CRUD ====================

@app.post("/api/certificate-requests")
async def create_certificate_request(csr: CertificateRequest):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO certificate_requests (gateway_code, key_id, csr_data, cert_type, status)
        VALUES (%s, %s, %s, %s, 'PENDING')
        """
        cursor.execute(query, (csr.gateway_code, csr.key_id, csr.csr_data, csr.cert_type))
        connection.commit()
        
        return {"status": "success", "message": f"{csr.cert_type} CSR submitted (PENDING)", "csr_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/certificate-requests")
async def get_all_certificate_requests(status: Optional[str] = None):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if status:
            cursor.execute("SELECT * FROM certificate_requests WHERE status = %s ORDER BY requested_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM certificate_requests ORDER BY requested_at DESC")
        
        csrs = cursor.fetchall()
        
        for csr in csrs:
            if csr.get('requested_at'):
                csr['requested_at'] = csr['requested_at'].isoformat()
        
        return {"status": "success", "total": len(csrs), "requests": csrs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/certificate-requests/{csr_id}")
async def get_certificate_request(csr_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM certificate_requests WHERE csr_id = %s", (csr_id,))
        csr = cursor.fetchone()
        
        if not csr:
            raise HTTPException(status_code=404, detail="CSR not found")
        
        if csr.get('requested_at'):
            csr['requested_at'] = csr['requested_at'].isoformat()
        
        # Normalize PEM data by ensuring proper line breaks
        if 'csr_data' in csr and csr['csr_data']:
            csr['csr_pem'] = normalize_pem_format(csr.pop('csr_data'))
        else:
            csr['csr_pem'] = csr.pop('csr_data', '')
        
        return {"status": "success", "request": csr}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/certificate-requests/{csr_id}")
async def update_certificate_request(csr_id: int, csr_update: CertificateRequestUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        if csr_update.status:
            cursor.execute(
                "UPDATE certificate_requests SET status = %s WHERE csr_id = %s",
                (csr_update.status, csr_id)
            )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="CSR not found")
        
        connection.commit()
        return {"status": "success", "message": "CSR updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/certificate-requests/{csr_id}")
async def delete_certificate_request(csr_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM certificate_requests WHERE csr_id = %s", (csr_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="CSR not found")
        
        connection.commit()
        return {"status": "success", "message": "CSR deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.post("/api/certificate-requests/{csr_id}/get-crt")
async def get_crt_from_csr(csr_id: int):
    """
    Convert CSR to CRT certificate via CA Management Service
    Calls CA service on port 9002 to generate certificate
    Automatically stores result in certificates table
    """
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Step 1: Get CSR details
        cursor.execute("SELECT * FROM certificate_requests WHERE csr_id = %s", (csr_id,))
        csr = cursor.fetchone()
        
        if not csr:
            raise HTTPException(status_code=404, detail="CSR not found")
        
        gateway_code = csr['gateway_code']
        key_id = csr['key_id']
        cert_type = csr['cert_type']
        
        # Step 2: Get server key (public key)
        cursor.execute("SELECT * FROM server_keys WHERE key_id = %s", (key_id,))
        server_key = cursor.fetchone()
        
        if not server_key:
            raise HTTPException(status_code=404, detail="Server key not found")
        
        public_key_pem = server_key['public_key']
        
        # Step 3: Get network config for server info
        cursor.execute("SELECT * FROM network_config WHERE gateway_code = %s", (gateway_code,))
        network_config = cursor.fetchone()
        
        if not network_config:
            raise HTTPException(status_code=404, detail="Network config not found")
        
        # Step 4: Call CA service to generate certificate
        ca_service_url = "http://localhost:9002/api/certificates"
        
        if cert_type == "AUTH":
            endpoint = f"{ca_service_url}/generate-auth"
        else:  # SIGN
            endpoint = f"{ca_service_url}/generate-sign"
        
        ca_request_payload = {
            "server_id": gateway_code,
            "server_name": network_config['hostname'] or gateway_code,
            "organization": network_config['environment'] or "Organization",
            "address": network_config['ip_address'] or "0.0.0.0",
            "public_key_pem": public_key_pem
        }
        
        # Make request to CA service
        ca_response = requests.post(endpoint, json=ca_request_payload, timeout=10)
        
        if ca_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"CA Service error: {ca_response.text}"
            )
        
        ca_data = ca_response.json()
        
        if ca_data.get("status") != "success":
            raise HTTPException(
                status_code=502,
                detail=f"CA Service failed: {ca_data.get('message', 'Unknown error')}"
            )
        
        # Step 5: Extract certificate from CA response
        certificate_pem = ca_data.get("certificate_pem")
        if not certificate_pem:
            raise HTTPException(status_code=502, detail="No certificate in CA response")
        
        issued_by = ca_data.get("issued_by", "CA Authority")
        valid_from = ca_data.get("issued_date", datetime.now().isoformat())
        valid_to = ca_data.get("expiry_date", datetime.now().isoformat())
        
        # Step 6: Store certificate in database
        insert_query = """
        INSERT INTO certificates 
        (gateway_code, key_id, cert_type, certificate, issued_by, valid_from, valid_to, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
        """
        
        cursor.execute(insert_query, (
            gateway_code, key_id, cert_type, certificate_pem,
            issued_by, valid_from, valid_to
        ))
        
        cert_id = cursor.lastrowid
        connection.commit()
        
        # Step 7: Update CSR status to SIGNED
        update_csr_query = "UPDATE certificate_requests SET status = 'SIGNED' WHERE csr_id = %s"
        cursor.execute(update_csr_query, (csr_id,))
        connection.commit()
        
        # Step 8: AUTO-ACTIVATION - Check if both AUTH and SIGN certificates are now ACTIVE
        # If both exist, automatically activate the security server
        cursor.execute(
            "SELECT cert_type, status FROM certificates WHERE gateway_code = %s AND cert_type IN ('AUTH', 'SIGN')",
            (gateway_code,)
        )
        existing_certs = cursor.fetchall()
        cert_types_active = {cert[0]: cert[1] for cert in existing_certs}
        
        # Check if both AUTH and SIGN certificates are ACTIVE
        if ('AUTH' in cert_types_active and 'SIGN' in cert_types_active and 
            cert_types_active['AUTH'] == 'ACTIVE' and cert_types_active['SIGN'] == 'ACTIVE'):
            
            # Both certificates are ACTIVE - activate the security server
            activate_query = "UPDATE network_config SET status = 'ACTIVE' WHERE gateway_code = %s"
            cursor.execute(activate_query, (gateway_code,))
            connection.commit()
            
            server_status = "ACTIVE"
            activation_message = "Both AUTH and SIGN certificates ACTIVE - Security Server ACTIVATED"
            
            # Log server activation
            log_administration_action(
                action_type="ACTIVATE_SECURITY_SERVER",
                performed_by="SYSTEM",
                target_entity=f"Gateway: {gateway_code}",
                status="SUCCESS",
                new_value="status=ACTIVE"
            )
        else:
            server_status = "INACTIVE"
            activation_message = f"Waiting for additional certificates. Currently have: {list(cert_types_active.keys())}"
        
        # Log certificate creation
        log_security_event(
            event_type="CERTIFICATE_CREATED",
            severity="MEDIUM",
            resource=f"CERTIFICATE:{cert_type}",
            action="CREATE",
            status="SUCCESS",
            user_id="SYSTEM",
            subsystem="CERTIFICATE_MANAGEMENT",
            certificate_id=cert_id
        )
        
        return {
            "status": "success",
            "message": "Certificate generated and stored successfully",
            "cert_id": cert_id,
            "csr_id": csr_id,
            "gateway_code": gateway_code,
            "cert_type": cert_type,
            "server_status": server_status,
            "activation_message": activation_message,
            "certificate": certificate_pem[:100] + "..." if len(certificate_pem) > 100 else certificate_pem
        }
    
    except requests.exceptions.ConnectionError:
        log_security_event(
            event_type="CERTIFICATE_GENERATION_FAILED",
            severity="CRITICAL",
            resource="CA_SERVICE",
            action="CONNECT",
            status="FAILED",
            failure_reason="Cannot connect to CA Service on port 9002"
        )
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to CA Service. Is it running on port 9002? Start it with: python CA_management/ca_service.py"
        )
    except requests.exceptions.Timeout:
        log_security_event(
            event_type="CERTIFICATE_GENERATION_FAILED",
            severity="HIGH",
            resource="CA_SERVICE",
            action="TIMEOUT",
            status="FAILED",
            failure_reason="CA Service request timeout"
        )
        raise HTTPException(status_code=504, detail="CA Service timeout")
    except Error as e:
        if connection:
            connection.rollback()
        log_security_event(
            event_type="CERTIFICATE_GENERATION_FAILED",
            severity="HIGH",
            resource="CERTIFICATE",
            action="CREATE",
            status="FAILED",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        log_security_event(
            event_type="CERTIFICATE_GENERATION_FAILED",
            severity="HIGH",
            resource="CERTIFICATE",
            action="CREATE",
            status="FAILED",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 5: CERTIFICATES CRUD ====================

@app.post("/api/certificates")
async def create_certificate(cert: Certificate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        INSERT INTO certificates 
        (gateway_code, key_id, cert_type, certificate, issued_by, valid_from, valid_to, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
        """
        cursor.execute(query, (
            cert.gateway_code, cert.key_id, cert.cert_type, cert.certificate,
            cert.issued_by, cert.valid_from, cert.valid_to
        ))
        cert_id = cursor.lastrowid
        connection.commit()
        
        # Auto-update certificate_requests status to SIGNED
        update_query = """
        UPDATE certificate_requests SET status = 'SIGNED' 
        WHERE gateway_code = %s AND cert_type = %s AND status = 'PENDING'
        """
        cursor.execute(update_query, (cert.gateway_code, cert.cert_type))
        connection.commit()
        
        # AUTO-ACTIVATION - Check if both AUTH and SIGN certificates are now ACTIVE
        cursor.execute(
            "SELECT cert_type, status FROM certificates WHERE gateway_code = %s AND cert_type IN ('AUTH', 'SIGN')",
            (cert.gateway_code,)
        )
        existing_certs = cursor.fetchall()
        cert_types_active = {c['cert_type']: c['status'] for c in existing_certs}
        
        activation_message = "Certificate stored"
        server_status = "INACTIVE"
        
        # Check if both AUTH and SIGN certificates are ACTIVE
        if ('AUTH' in cert_types_active and 'SIGN' in cert_types_active and 
            cert_types_active['AUTH'] == 'ACTIVE' and cert_types_active['SIGN'] == 'ACTIVE'):
            
            # Both certificates are ACTIVE - activate the security server
            activate_query = "UPDATE network_config SET status = 'ACTIVE' WHERE gateway_code = %s"
            cursor.execute(activate_query, (cert.gateway_code,))
            connection.commit()
            
            server_status = "ACTIVE"
            activation_message = "Both AUTH and SIGN certificates ACTIVE - Security Server ACTIVATED"
            
            # Log server activation
            log_administration_action(
                action_type="ACTIVATE_SECURITY_SERVER",
                performed_by="SYSTEM",
                target_entity=f"Gateway: {cert.gateway_code}",
                status="SUCCESS",
                new_value="status=ACTIVE"
            )
        else:
            activation_message = f"Waiting for additional certificates. Currently have: {list(cert_types_active.keys())}"
        
        # Log certificate creation
        log_security_event(
            event_type="CERTIFICATE_CREATED",
            severity="MEDIUM",
            resource=f"CERTIFICATE:{cert.cert_type}",
            action="CREATE",
            status="SUCCESS",
            user_id="SYSTEM",
            subsystem="CERTIFICATE_MANAGEMENT",
            certificate_id=cert_id
        )
        
        return {
            "status": "success",
            "message": f"{cert.cert_type} certificate stored (ACTIVE)",
            "cert_id": cert_id,
            "server_status": server_status,
            "activation_message": activation_message
        }
    except Error as e:
        if connection:
            connection.rollback()
        # Log certificate creation error
        log_security_event(
            event_type="CERTIFICATE_CREATION_FAILED",
            severity="HIGH",
            resource="CERTIFICATE",
            action="CREATE",
            status="FAILED",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.post("/api/certificates/save-signed-certificate")
async def save_signed_certificate(request: SaveSignedCertificateRequest):
    """
    Save signed certificate from CA service
    Updates: certificates table, certificate_requests status, and global_directory
    """
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        csr_id = request.csr_id
        ca_response = request.ca_response
        
        # Get CSR details
        cursor.execute("SELECT gateway_code, key_id, cert_type FROM certificate_requests WHERE csr_id = %s", (csr_id,))
        csr = cursor.fetchone()
        
        if not csr:
            raise HTTPException(status_code=404, detail="CSR not found")
        
        gateway_code = csr['gateway_code']
        key_id = csr['key_id']
        cert_type = csr['cert_type']
        
        # Verify key_id exists in server_keys table (optional reference)
        # If not, set to NULL to avoid foreign key constraint issues
        if key_id:
            cursor.execute("SELECT key_id FROM server_keys WHERE key_id = %s", (key_id,))
            if not cursor.fetchone():
                # Key doesn't exist, set to NULL for the certificate
                key_id = None
        
        # Extract certificate details from CA response
        certificate_pem = ca_response.get('certificate_pem', '')
        issued_date_str = ca_response.get('issued_date', datetime.now().isoformat())
        expiry_date_str = ca_response.get('expiry_date', (datetime.now().replace(year=datetime.now().year + 1)).isoformat())
        
        # Parse ISO format dates to MySQL DATETIME format (YYYY-MM-DD HH:MM:SS)
        try:
            if isinstance(issued_date_str, str) and 'T' in issued_date_str:
                # Convert ISO format to MySQL datetime format
                issued_date = issued_date_str.split('T')[0] + ' ' + issued_date_str.split('T')[1].split('+')[0].split('Z')[0]
            else:
                issued_date = issued_date_str
            
            if isinstance(expiry_date_str, str) and 'T' in expiry_date_str:
                expiry_date = expiry_date_str.split('T')[0] + ' ' + expiry_date_str.split('T')[1].split('+')[0].split('Z')[0]
            else:
                expiry_date = expiry_date_str
        except Exception as date_err:
            # Fallback to current time if parsing fails
            issued_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            expiry_date = (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert into certificates table
        cert_query = """
        INSERT INTO certificates 
        (gateway_code, key_id, cert_type, certificate, issued_by, valid_from, valid_to, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
        """
        cursor.execute(cert_query, (
            gateway_code,
            key_id,
            cert_type,
            certificate_pem,
            'CA Authority',
            issued_date,
            expiry_date
        ))
        cert_db_id = cursor.lastrowid
        connection.commit()
        
        # Update certificate_requests status to SIGNED
        update_csr_query = "UPDATE certificate_requests SET status = 'SIGNED' WHERE csr_id = %s"
        cursor.execute(update_csr_query, (csr_id,))
        connection.commit()
        
        # AUTO-ACTIVATION - Check if both AUTH and SIGN certificates are now ACTIVE
        cursor.execute(
            "SELECT cert_type, status FROM certificates WHERE gateway_code = %s AND cert_type IN ('AUTH', 'SIGN')",
            (gateway_code,)
        )
        existing_certs = cursor.fetchall()
        cert_types_active = {c['cert_type']: c['status'] for c in existing_certs}
        
        activation_message = "Certificate saved"
        server_status = "INACTIVE"
        
        # Check if both AUTH and SIGN certificates are ACTIVE
        if ('AUTH' in cert_types_active and 'SIGN' in cert_types_active and 
            cert_types_active['AUTH'] == 'ACTIVE' and cert_types_active['SIGN'] == 'ACTIVE'):
            
            # Both certificates are ACTIVE - activate the security server
            activate_query = "UPDATE network_config SET status = 'ACTIVE' WHERE gateway_code = %s"
            cursor.execute(activate_query, (gateway_code,))
            connection.commit()
            
            server_status = "ACTIVE"
            activation_message = "Both AUTH and SIGN certificates ACTIVE - Security Server ACTIVATED"
        
        # Update or insert into global_directory (optional - skip if table has constraints)
        try:
            cursor.execute("SELECT directory_id FROM global_directory WHERE gateway_code = %s", (gateway_code,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                if cert_type.upper() == 'AUTH':
                    update_dir_query = """
                    UPDATE global_directory SET auth_cert_id = %s, status = %s
                    WHERE gateway_code = %s
                    """
                    cursor.execute(update_dir_query, (cert_db_id, server_status, gateway_code))
                else:  # SIGN
                    update_dir_query = """
                    UPDATE global_directory SET sign_cert_id = %s, status = %s
                    WHERE gateway_code = %s
                    """
                    cursor.execute(update_dir_query, (cert_db_id, server_status, gateway_code))
            else:
                # Get entity_code from network_config
                cursor.execute("SELECT entity_id FROM network_config WHERE gateway_code = %s", (gateway_code,))
                nc = cursor.fetchone()
                entity_code = nc.get('entity_id', 'UNKNOWN') if nc else 'UNKNOWN'
                
                # Insert new entry
                if cert_type.upper() == 'AUTH':
                    insert_dir_query = """
                    INSERT INTO global_directory 
                    (entity_code, gateway_code, auth_cert_id, status)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_dir_query, (entity_code, gateway_code, cert_db_id, server_status))
                else:  # SIGN
                    insert_dir_query = """
                    INSERT INTO global_directory 
                    (entity_code, gateway_code, sign_cert_id, status)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_dir_query, (entity_code, gateway_code, cert_db_id, server_status))
            
            connection.commit()
        except Exception as dir_err:
            # Skip global_directory update if it fails (likely missing constraints)
            print(f"[WARNING] Failed to update global_directory: {str(dir_err)}")
        
        return {
            "status": "success",
            "message": f"{cert_type} certificate saved successfully",
            "cert_id": cert_db_id,
            "server_status": server_status,
            "activation_message": activation_message,
            "certificate_pem": certificate_pem
        }
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/certificates")
async def get_all_certificates():
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM certificates ORDER BY created_at DESC")
        certs = cursor.fetchall()
        
        for cert in certs:
            if cert.get('created_at'):
                cert['created_at'] = cert['created_at'].isoformat()
            if cert.get('valid_from'):
                cert['valid_from'] = cert['valid_from'].isoformat()
            if cert.get('valid_to'):
                cert['valid_to'] = cert['valid_to'].isoformat()
        
        return {"status": "success", "total": len(certs), "certificates": certs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/certificates/{cert_id}")
async def get_certificate(cert_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM certificates WHERE cert_id = %s", (cert_id,))
        cert = cursor.fetchone()
        
        if not cert:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        if cert.get('created_at'):
            cert['created_at'] = cert['created_at'].isoformat()
        if cert.get('valid_from'):
            cert['valid_from'] = cert['valid_from'].isoformat()
        if cert.get('valid_to'):
            cert['valid_to'] = cert['valid_to'].isoformat()
        
        return {"status": "success", "certificate": cert}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/certificates/gateway/{gateway_code}")
async def get_certificates_by_gateway(gateway_code: str):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM certificates WHERE gateway_code = %s ORDER BY created_at", (gateway_code,))
        certs = cursor.fetchall()
        
        for cert in certs:
            if cert.get('created_at'):
                cert['created_at'] = cert['created_at'].isoformat()
            if cert.get('valid_from'):
                cert['valid_from'] = cert['valid_from'].isoformat()
            if cert.get('valid_to'):
                cert['valid_to'] = cert['valid_to'].isoformat()
        
        return {"status": "success", "gateway_code": gateway_code, "total": len(certs), "certificates": certs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/registration-status/{gateway_code}")
async def check_registration_status(gateway_code: str):
    """Check registration status for a gateway. Returns ACTIVE if both AUTH and SIGN certificates exist."""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get network config
        cursor.execute("SELECT * FROM network_config WHERE gateway_code = %s", (gateway_code,))
        network_config = cursor.fetchone()
        
        if not network_config:
            raise HTTPException(status_code=404, detail=f"Gateway {gateway_code} not found")
        
        # Check for AUTH and SIGN certificates
        cursor.execute(
            "SELECT cert_type FROM certificates WHERE gateway_code = %s AND cert_type IN ('AUTH', 'SIGN')",
            (gateway_code,)
        )
        certs = cursor.fetchall()
        cert_types = {cert['cert_type'] for cert in certs}
        
        # If both certificates exist, update status to ACTIVE and return certificates
        if 'AUTH' in cert_types and 'SIGN' in cert_types:
            # Update network_config status to ACTIVE
            update_query = "UPDATE network_config SET status = 'ACTIVE' WHERE gateway_code = %s"
            cursor.execute(update_query, (gateway_code,))
            connection.commit()
            
            # Get all certificates for this gateway
            cursor.execute(
                "SELECT * FROM certificates WHERE gateway_code = %s ORDER BY created_at",
                (gateway_code,)
            )
            certificates = cursor.fetchall()
            
            for cert in certificates:
                if cert.get('created_at'):
                    cert['created_at'] = cert['created_at'].isoformat()
                if cert.get('valid_from'):
                    cert['valid_from'] = cert['valid_from'].isoformat()
                if cert.get('valid_to'):
                    cert['valid_to'] = cert['valid_to'].isoformat()
            
            return {
                "status": "success",
                "registration_status": "ACTIVE",
                "gateway_code": gateway_code,
                "certificates": certificates,
                "auth_cert": next((c for c in certificates if c['cert_type'] == 'AUTH'), None),
                "sign_cert": next((c for c in certificates if c['cert_type'] == 'SIGN'), None)
            }
        else:
            # Missing one or both certificates
            return {
                "status": "success",
                "registration_status": "INACTIVE",
                "gateway_code": gateway_code,
                "message": "Waiting for certificate generation",
                "certificates_pending": ['AUTH', 'SIGN'] if not cert_types else list(set(['AUTH', 'SIGN']) - cert_types),
                "certificates_received": list(cert_types)
            }
    except HTTPException:
        raise
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/certificates/{cert_id}")
async def update_certificate(cert_id: int, cert_update: CertificateUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        if cert_update.status:
            cursor.execute(
                "UPDATE certificates SET status = %s WHERE cert_id = %s",
                (cert_update.status, cert_id)
            )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        connection.commit()
        return {"status": "success", "message": "Certificate updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/certificates/{cert_id}")
async def delete_certificate(cert_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM certificates WHERE cert_id = %s", (cert_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        connection.commit()
        return {"status": "success", "message": "Certificate deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 6: REGISTRATION_LOG CRUD ====================

@app.post("/api/registration-log")
async def create_registration_log(log: RegistrationLog):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO registration_log (gateway_code, action, performed_by, remarks)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (log.gateway_code, log.action, log.performed_by, log.remarks))
        connection.commit()
        
        connection.commit()
        
        return {"status": "success", "message": f"Action logged: {log.action}", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/registration-log")
async def get_all_registration_logs(action: Optional[str] = None):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if action:
            cursor.execute("SELECT * FROM registration_log WHERE action = %s ORDER BY created_at DESC", (action,))
        else:
            cursor.execute("SELECT * FROM registration_log ORDER BY created_at DESC")
        
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('created_at'):
                log['created_at'] = log['created_at'].isoformat()
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/registration-log/{log_id}")
async def get_registration_log(log_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM registration_log WHERE log_id = %s", (log_id,))
        log = cursor.fetchone()
        
        if not log:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        if log.get('created_at'):
            log['created_at'] = log['created_at'].isoformat()
        
        return {"status": "success", "log": log}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/registration-log/gateway/{gateway_code}")
async def get_registration_logs_by_gateway(gateway_code: str):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM registration_log WHERE gateway_code = %s ORDER BY created_at DESC", (gateway_code,))
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('created_at'):
                log['created_at'] = log['created_at'].isoformat()
        
        return {"status": "success", "gateway_code": gateway_code, "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/registration-log/{log_id}")
async def update_registration_log(log_id: int, log_update: RegistrationLogUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        update_fields = []
        values = []
        
        for field, value in log_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = %s")
            values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(log_id)
        query = f"UPDATE registration_log SET {', '.join(update_fields)} WHERE log_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        connection.commit()
        return {"status": "success", "message": "Log updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/registration-log/{log_id}")
async def delete_registration_log(log_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM registration_log WHERE log_id = %s", (log_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        connection.commit()
        return {"status": "success", "message": "Log entry deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 7: GLOBAL_DIRECTORY CRUD ====================

@app.post("/api/global-directory")
async def create_global_directory_entry(entry: GlobalDirectoryEntry):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Verify gateway exists
        check_query = "SELECT gateway_code FROM network_config WHERE gateway_code = %s"
        cursor.execute(check_query, (entry.gateway_code,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Gateway not found")
        
        query = """
        INSERT INTO global_directory 
        (entity_code, gateway_code, service_url, auth_cert_id, sign_cert_id, status)
        VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
        """
        cursor.execute(query, (
            entry.entity_code, entry.gateway_code, entry.service_url,
            entry.auth_cert_id, entry.sign_cert_id
        ))
        connection.commit()
        
        return {"status": "success", "message": "Published to global directory (ACTIVE)", "directory_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/global-directory")
async def get_all_global_directory_entries(status: Optional[str] = None):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT gd.*, e.entity_name, nc.host, nc.port, nc.hostname
        FROM global_directory gd
        JOIN entities e ON gd.entity_code = e.entity_code
        JOIN network_config nc ON gd.gateway_code = nc.gateway_code
        ORDER BY gd.created_at DESC
        """
        cursor.execute(query)
        
        entries = cursor.fetchall()
        
        for entry in entries:
            if entry.get('created_at'):
                entry['created_at'] = entry['created_at'].isoformat()
        
        return {"status": "success", "message": "Global Directory", "total": len(entries), "directory": entries}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/security-servers-with-certificates")
async def get_security_servers_with_certificates():
    """Get security servers with their certificate information from global_directory"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query global_directory which has all servers and their certificates
        query = """
        SELECT 
            gd.directory_id as id,
            gd.gateway_code as name,
            gd.entity_code,
            gd.service_url,
            gd.auth_cert_id,
            gd.sign_cert_id,
            gd.status as directory_status
        FROM global_directory gd
        ORDER BY gd.gateway_code
        """
        cursor.execute(query)
        servers = cursor.fetchall()
        
        return servers
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/global-directory/{directory_id}")
async def get_global_directory_entry(directory_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT gd.*, e.entity_name, nc.host, nc.port, nc.hostname
        FROM global_directory gd
        JOIN entities e ON gd.entity_code = e.entity_code
        JOIN network_config nc ON gd.gateway_code = nc.gateway_code
        WHERE gd.directory_id = %s
        """
        cursor.execute(query, (directory_id,))
        entry = cursor.fetchone()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Directory entry not found")
        
        if entry.get('created_at'):
            entry['created_at'] = entry['created_at'].isoformat()
        
        return {"status": "success", "entry": entry}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/global-directory/{directory_id}")
async def update_global_directory_entry(directory_id: int, entry_update: GlobalDirectoryUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        update_fields = []
        values = []
        
        for field, value in entry_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = %s")
            values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(directory_id)
        query = f"UPDATE global_directory SET {', '.join(update_fields)} WHERE directory_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Directory entry not found")
        
        connection.commit()
        return {"status": "success", "message": "Directory entry updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/global-directory/{directory_id}")
async def delete_global_directory_entry(directory_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM global_directory WHERE directory_id = %s", (directory_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Directory entry not found")
        
        connection.commit()
        return {"status": "success", "message": "Directory entry deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 8: SUBSYSTEMS CRUD ====================

@app.post("/api/subsystems")
async def create_subsystem(subsystem: Subsystem):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    cursor = None
    try:
        print("\n[DEBUG] POST /api/subsystems")
        print(f"[DEBUG] Received data: entity_id={subsystem.entity_id}, subsystem_code={subsystem.subsystem_code}, subsystem_name={subsystem.subsystem_name}")
        
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Validate entity_id exists
        cursor.execute("SELECT entity_id FROM entities WHERE entity_id = %s", (subsystem.entity_id,))
        if not cursor.fetchone():
            error_msg = f"Entity ID {subsystem.entity_id} does not exist"
            print(f"[ERROR] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        print(f"[DEBUG] ✓ Entity ID {subsystem.entity_id} found")
        
        query = """
        INSERT INTO subsystems (entity_id, subsystem_code, subsystem_name, description, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        print(f"[DEBUG] Executing INSERT query...")
        cursor.execute(query, (subsystem.entity_id, subsystem.subsystem_code, subsystem.subsystem_name, 
                               subsystem.description, subsystem.status))
        connection.commit()
        
        subsystem_id = cursor.lastrowid
        print(f"[DEBUG] ✓ Subsystem created successfully with ID: {subsystem_id}")
        
        return {"status": "success", "message": "Subsystem created", "subsystem_id": subsystem_id}
    except HTTPException as http_err:
        print(f"[ERROR] HTTP Exception: {http_err.detail}")
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise
    except Error as e:
        error_msg = f"Database Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Error Type: {type(e).__name__}")
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Error Type: {type(e).__name__}")
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()


@app.get("/api/subsystems")
async def get_all_subsystems():
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT s.*, e.entity_code, e.entity_name 
            FROM subsystems s
            LEFT JOIN entities e ON s.entity_id = e.entity_id
            ORDER BY s.created_at DESC
        """)
        subsystems = cursor.fetchall()
        
        for subsystem in subsystems:
            if subsystem.get('created_at'):
                subsystem['created_at'] = subsystem['created_at'].isoformat()
            if subsystem.get('updated_at'):
                subsystem['updated_at'] = subsystem['updated_at'].isoformat()
        
        return subsystems
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/subsystems/{subsystem_id}")
async def get_subsystem(subsystem_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT s.*, e.entity_code, e.entity_name 
            FROM subsystems s
            LEFT JOIN entities e ON s.entity_id = e.entity_id
            WHERE s.subsystem_id = %s
        """, (subsystem_id,))
        subsystem = cursor.fetchone()
        
        if not subsystem:
            raise HTTPException(status_code=404, detail="Subsystem not found")
        
        if subsystem.get('created_at'):
            subsystem['created_at'] = subsystem['created_at'].isoformat()
        if subsystem.get('updated_at'):
            subsystem['updated_at'] = subsystem['updated_at'].isoformat()
        
        return {"status": "success", "subsystem": subsystem}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/subsystems/{subsystem_id}")
async def update_subsystem(subsystem_id: int, subsystem: SubsystemUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Build dynamic update query
        updates = []
        values = []
        
        if subsystem.entity_id is not None:
            updates.append("entity_id = %s")
            values.append(subsystem.entity_id)
        if subsystem.subsystem_code is not None:
            updates.append("subsystem_code = %s")
            values.append(subsystem.subsystem_code)
        if subsystem.subsystem_name is not None:
            updates.append("subsystem_name = %s")
            values.append(subsystem.subsystem_name)
        if subsystem.description is not None:
            updates.append("description = %s")
            values.append(subsystem.description)
        if subsystem.status is not None:
            updates.append("status = %s")
            values.append(subsystem.status)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updates.append("updated_at = NOW()")
        values.append(subsystem_id)
        
        query = f"UPDATE subsystems SET {', '.join(updates)} WHERE subsystem_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subsystem not found")
        
        connection.commit()
        return {"status": "success", "message": "Subsystem updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/subsystems/{subsystem_id}")
async def delete_subsystem(subsystem_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM subsystems WHERE subsystem_id = %s", (subsystem_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subsystem not found")
        
        connection.commit()
        return {"status": "success", "message": "Subsystem deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 9: GLOBAL_SERVICE_REGISTER CRUD ====================

@app.post("/api/global-service-register")
async def create_global_service(service: GlobalServiceRegister):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    cursor = None
    try:
        print("\n[DEBUG] POST /api/global-service-register")
        print(f"[DEBUG] Received data: entity_id={service.entity_id}, subsystem_id={service.subsystem_id}, service_code={service.service_code}")
        
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Validate entity_id exists
        cursor.execute("SELECT entity_id FROM entities WHERE entity_id = %s", (service.entity_id,))
        if not cursor.fetchone():
            error_msg = f"Entity ID {service.entity_id} does not exist"
            print(f"[ERROR] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        print(f"[DEBUG] ✓ Entity ID {service.entity_id} found")
        
        # Validate subsystem_id exists
        cursor.execute("SELECT subsystem_id FROM subsystems WHERE subsystem_id = %s", (service.subsystem_id,))
        if not cursor.fetchone():
            error_msg = f"Subsystem ID {service.subsystem_id} does not exist"
            print(f"[ERROR] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        print(f"[DEBUG] ✓ Subsystem ID {service.subsystem_id} found")
        
        # Validate security_server_id exists if provided
        if service.security_server_id:
            cursor.execute("SELECT id FROM network_config WHERE id = %s", (service.security_server_id,))
            if not cursor.fetchone():
                error_msg = f"Security Server ID {service.security_server_id} does not exist"
                print(f"[ERROR] {error_msg}")
                raise HTTPException(status_code=400, detail=error_msg)
            print(f"[DEBUG] ✓ Security Server ID {service.security_server_id} found")
        
        query = """
        INSERT INTO global_service_register 
        (entity_id, subsystem_id, service_code, service_name, service_version, full_service_id, 
         service_url, http_method, protocol, security_server_id, description, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        print(f"[DEBUG] Executing INSERT query...")
        cursor.execute(query, (service.entity_id, service.subsystem_id, service.service_code, 
                               service.service_name, service.service_version, service.full_service_id,
                               service.service_url, service.http_method, service.protocol, 
                               service.security_server_id, service.description, service.status))
        connection.commit()
        
        service_id = cursor.lastrowid
        print(f"[DEBUG] ✓ Service registered successfully with ID: {service_id}")
        
        return {"status": "success", "message": "Global service registered", "service_id": service_id}
    except HTTPException as http_err:
        print(f"[ERROR] HTTP Exception: {http_err.detail}")
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise
    except Error as e:
        error_msg = f"Database Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Error Type: {type(e).__name__}")
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Error Type: {type(e).__name__}")
        if connection:
            try:
                connection.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()


@app.get("/api/global-service-register")
async def get_all_global_services():
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT g.*, e.entity_code, e.entity_name, s.subsystem_code, s.subsystem_name, n.title as server_title
            FROM global_service_register g
            LEFT JOIN entities e ON g.entity_id = e.entity_id
            LEFT JOIN subsystems s ON g.subsystem_id = s.subsystem_id
            LEFT JOIN network_config n ON g.security_server_id = n.id
            ORDER BY g.created_at DESC
        """)
        services = cursor.fetchall()
        
        for service in services:
            if service.get('created_at'):
                service['created_at'] = service['created_at'].isoformat()
            if service.get('updated_at'):
                service['updated_at'] = service['updated_at'].isoformat()
        
        return services
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/global-service-register/{service_id}")
async def get_global_service(service_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT g.*, e.entity_code, e.entity_name, s.subsystem_code, s.subsystem_name, n.title as server_title
            FROM global_service_register g
            LEFT JOIN entities e ON g.entity_id = e.entity_id
            LEFT JOIN subsystems s ON g.subsystem_id = s.subsystem_id
            LEFT JOIN network_config n ON g.security_server_id = n.id
            WHERE g.service_id = %s
        """, (service_id,))
        service = cursor.fetchone()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        if service.get('created_at'):
            service['created_at'] = service['created_at'].isoformat()
        if service.get('updated_at'):
            service['updated_at'] = service['updated_at'].isoformat()
        
        return {"status": "success", "service": service}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/global-service-register/{service_id}")
async def update_global_service(service_id: int, service: GlobalServiceRegisterUpdate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Build dynamic update query
        updates = []
        values = []
        
        if service.entity_id is not None:
            updates.append("entity_id = %s")
            values.append(service.entity_id)
        if service.subsystem_id is not None:
            updates.append("subsystem_id = %s")
            values.append(service.subsystem_id)
        if service.service_code is not None:
            updates.append("service_code = %s")
            values.append(service.service_code)
        if service.service_name is not None:
            updates.append("service_name = %s")
            values.append(service.service_name)
        if service.service_version is not None:
            updates.append("service_version = %s")
            values.append(service.service_version)
        if service.full_service_id is not None:
            updates.append("full_service_id = %s")
            values.append(service.full_service_id)
        if service.service_url is not None:
            updates.append("service_url = %s")
            values.append(service.service_url)
        if service.http_method is not None:
            updates.append("http_method = %s")
            values.append(service.http_method)
        if service.protocol is not None:
            updates.append("protocol = %s")
            values.append(service.protocol)
        if service.security_server_id is not None:
            updates.append("security_server_id = %s")
            values.append(service.security_server_id)
        if service.description is not None:
            updates.append("description = %s")
            values.append(service.description)
        if service.status is not None:
            updates.append("status = %s")
            values.append(service.status)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updates.append("updated_at = NOW()")
        values.append(service_id)
        
        query = f"UPDATE global_service_register SET {', '.join(updates)} WHERE service_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        
        connection.commit()
        return {"status": "success", "message": "Service updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/global-service-register/{service_id}")
async def delete_global_service(service_id: int):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM global_service_register WHERE service_id = %s", (service_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        
        connection.commit()
        return {"status": "success", "message": "Service deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== PUBLIC SERVICE DISCOVERY API ====================

@app.get("/api/public/services")
async def get_available_services(entity_code: Optional[str] = None, subsystem_code: Optional[str] = None):
    """
    Public API endpoint to discover available services
    Returns all ACTIVE services with their details
    Optional filters: entity_code, subsystem_code
    """
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                g.service_id,
                g.service_code,
                g.service_name,
                g.service_version,
                g.full_service_id,
                g.service_url,
                g.http_method,
                g.protocol,
                g.description,
                g.status,
                e.entity_code,
                e.entity_name,
                e.entity_type,
                s.subsystem_code,
                s.subsystem_name,
                n.gateway_code as security_server_code,
                n.title as security_server_title,
                g.created_at,
                g.updated_at
            FROM global_service_register g
            LEFT JOIN entities e ON g.entity_id = e.entity_id
            LEFT JOIN subsystems s ON g.subsystem_id = s.subsystem_id
            LEFT JOIN network_config n ON g.security_server_id = n.id
            WHERE g.status = 'ACTIVE'
        """
        
        params = []
        
        if entity_code:
            query += " AND e.entity_code = %s"
            params.append(entity_code)
        
        if subsystem_code:
            query += " AND s.subsystem_code = %s"
            params.append(subsystem_code)
        
        query += " ORDER BY e.entity_code, s.subsystem_code, g.service_code"
        
        cursor.execute(query, params)
        services = cursor.fetchall()
        
        # Format timestamps
        for service in services:
            if service.get('created_at'):
                service['created_at'] = service['created_at'].isoformat()
            if service.get('updated_at'):
                service['updated_at'] = service['updated_at'].isoformat()
        
        return {
            "status": "success",
            "total": len(services),
            "services": services
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/public/services/{entity_code}/{subsystem_code}/{service_code}")
async def get_service_by_codes(entity_code: str, subsystem_code: str, service_code: str):
    """
    Get a specific service by entity, subsystem, and service codes
    Returns service details if ACTIVE
    """
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                g.service_id,
                g.service_code,
                g.service_name,
                g.service_version,
                g.full_service_id,
                g.service_url,
                g.http_method,
                g.protocol,
                g.description,
                g.status,
                e.entity_code,
                e.entity_name,
                e.entity_type,
                s.subsystem_code,
                s.subsystem_name,
                n.gateway_code as security_server_code,
                n.title as security_server_title,
                g.created_at,
                g.updated_at
            FROM global_service_register g
            LEFT JOIN entities e ON g.entity_id = e.entity_id
            LEFT JOIN subsystems s ON g.subsystem_id = s.subsystem_id
            LEFT JOIN network_config n ON g.security_server_id = n.id
            WHERE g.status = 'ACTIVE'
            AND e.entity_code = %s
            AND s.subsystem_code = %s
            AND g.service_code = %s
        """
        
        cursor.execute(query, (entity_code, subsystem_code, service_code))
        service = cursor.fetchone()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found or inactive")
        
        if service.get('created_at'):
            service['created_at'] = service['created_at'].isoformat()
        if service.get('updated_at'):
            service['updated_at'] = service['updated_at'].isoformat()
        
        return {
            "status": "success",
            "service": service
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== Database Initialization ====================

@app.post("/api/init-db")
async def initialize_database():
    """Initialize all database tables"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        # Create tables
        tables = {
            "entities": """
            CREATE TABLE IF NOT EXISTS entities (
                entity_id INT AUTO_INCREMENT PRIMARY KEY,
                entity_code VARCHAR(50) UNIQUE NOT NULL,
                entity_name VARCHAR(255) NOT NULL,
                entity_type VARCHAR(50),
                status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                request_status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING'
            )
            """,
            
            "network_config": """
            CREATE TABLE IF NOT EXISTS network_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                gateway_code VARCHAR(50) UNIQUE NOT NULL,
                entity_id INT NOT NULL,
                title VARCHAR(255),
                version VARCHAR(50),
                network_instance VARCHAR(50),
                host VARCHAR(255),
                port INT,
                hostname VARCHAR(255),
                ip_address VARCHAR(50),
                environment VARCHAR(50),
                status VARCHAR(20) DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE
            )
            """,
            
            "server_keys": """
            CREATE TABLE IF NOT EXISTS server_keys (
                key_id INT AUTO_INCREMENT PRIMARY KEY,
                gateway_code VARCHAR(50) NOT NULL,
                key_type VARCHAR(20),
                public_key LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (gateway_code)
            )
            """,
            
            "certificate_requests": """
            CREATE TABLE IF NOT EXISTS certificate_requests (
                csr_id INT AUTO_INCREMENT PRIMARY KEY,
                gateway_code VARCHAR(50) NOT NULL,
                key_id INT,
                csr_data LONGTEXT,
                cert_type VARCHAR(20),
                status VARCHAR(20) DEFAULT 'PENDING',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (gateway_code)
            )
            """,
            
            "certificates": """
            CREATE TABLE IF NOT EXISTS certificates (
                cert_id INT AUTO_INCREMENT PRIMARY KEY,
                gateway_code VARCHAR(50) NOT NULL,
                key_id INT,
                cert_type VARCHAR(20),
                certificate LONGTEXT,
                issued_by VARCHAR(255),
                valid_from DATETIME,
                valid_to DATETIME,
                status VARCHAR(20) DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code),
                FOREIGN KEY (key_id) REFERENCES server_keys(key_id) ON DELETE SET NULL
            )
            """,
            
            "registration_log": """
            CREATE TABLE IF NOT EXISTS registration_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                gateway_code VARCHAR(50) NOT NULL,
                action VARCHAR(50),
                performed_by VARCHAR(255),
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
            )
            """,
            
            "global_directory": """
            CREATE TABLE IF NOT EXISTS global_directory (
                directory_id INT AUTO_INCREMENT PRIMARY KEY,
                entity_code VARCHAR(50) NOT NULL,
                gateway_code VARCHAR(50) NOT NULL,
                service_url VARCHAR(255),
                auth_cert_id INT,
                sign_cert_id INT,
                status VARCHAR(20) DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_code) REFERENCES entities(entity_code),
                FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
            )
            """,
            
            "subsystems": """
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
                UNIQUE KEY unique_subsystem (entity_id, subsystem_code)
            )
            """,
            
            "global_service_register": """
            CREATE TABLE IF NOT EXISTS global_service_register (
                service_id INT AUTO_INCREMENT PRIMARY KEY,
                entity_id INT NOT NULL,
                subsystem_id INT NOT NULL,
                service_code VARCHAR(100) NOT NULL,
                service_name VARCHAR(255) NOT NULL,
                service_version VARCHAR(50),
                full_service_id VARCHAR(500),
                service_url VARCHAR(500),
                http_method VARCHAR(10),
                protocol VARCHAR(20),
                security_server_id INT,
                description TEXT,
                status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
                FOREIGN KEY (subsystem_id) REFERENCES subsystems(subsystem_id) ON DELETE CASCADE,
                FOREIGN KEY (security_server_id) REFERENCES network_config(id) ON DELETE SET NULL,
                UNIQUE KEY unique_service (entity_id, subsystem_id, service_code)
            )
            """
        }
        
        created_tables = []
        for table_name, table_schema in tables.items():
            try:
                cursor.execute(table_schema)
                created_tables.append(table_name)
            except Error as e:
                if "already exists" not in str(e):
                    raise
        
        connection.commit()
        
        return {
            "status": "success",
            "message": "Database initialized",
            "tables_created": created_tables,
            "total_tables": len(tables)
        }
    
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== Frontend Compatibility Endpoints ====================

@app.get("/api/security-entities")
async def get_security_entities(entity_type: Optional[str] = None):
    """Get security entities (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if entity_type:
            cursor.execute("SELECT * FROM entities WHERE entity_type = %s ORDER BY created_at DESC", (entity_type,))
        else:
            cursor.execute("SELECT * FROM entities ORDER BY created_at DESC")
        
        entities = cursor.fetchall()
        
        # Transform field names for frontend compatibility
        result = []
        for entity in entities:
            result.append({
                "id": entity['entity_id'],
                "code": entity['entity_code'],
                "name": entity['entity_name'],
                "type": entity['entity_type'],
                "status": entity['status'],
                "description": "",
                "version": "1.0",
                "contact_email": "",
                "tags": ""
            })
        
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.post("/api/security-entities")
async def create_security_entity(request: Any = Body(...)):
    """Create security entity (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    if request is None:
        raise HTTPException(status_code=400, detail="Request body is required")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        entity_code = request.get('id') or request.get('code', '')
        entity_name = request.get('name', '')
        entity_type = request.get('type', request.get('entity_type', 'security_server'))
        status = request.get('status', 'ACTIVE')
        
        query = """
        INSERT INTO entities (entity_code, entity_name, entity_type, status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (entity_code, entity_name, entity_type, status))
        connection.commit()
        
        return {"status": "success", "message": "Entity created", "entity_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/security-entities/{entity_id}")
async def get_security_entity(entity_id: int):
    """Get specific security entity (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM entities WHERE entity_id = %s", (entity_id,))
        entity = cursor.fetchone()
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Transform field names for frontend compatibility
        return {
            "id": entity['entity_id'],
            "code": entity['entity_code'],
            "name": entity['entity_name'],
            "type": entity['entity_type'],
            "status": entity['status'],
            "description": "",
            "version": "1.0",
            "contact_email": "",
            "tags": ""
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/security-entities/{entity_id}")
async def update_security_entity(entity_id: int, request: Any = Body(...)):
    """Update security entity (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    if request is None:
        raise HTTPException(status_code=400, detail="Request body is required")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        entity_code = request.get('code', '')
        entity_name = request.get('name', '')
        entity_type = request.get('type', request.get('entity_type', 'security_server'))
        status = request.get('status', 'ACTIVE')
        
        query = """
        UPDATE entities 
        SET entity_code=%s, entity_name=%s, entity_type=%s, status=%s
        WHERE entity_id=%s
        """
        cursor.execute(query, (entity_code, entity_name, entity_type, status, entity_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        connection.commit()
        return {"status": "success", "message": "Entity updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/security-entities/{entity_id}")
async def delete_security_entity(entity_id: int):
    """Delete security entity (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM entities WHERE entity_id = %s", (entity_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        connection.commit()
        return {"status": "success", "message": "Entity deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== Registration Approvals (Alias for Registration Log) ====================

@app.get("/api/registration-approvals")
async def get_registration_approvals(status: Optional[str] = None):
    """Get registration approvals (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if status:
            cursor.execute("SELECT * FROM registration_log WHERE action = %s ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM registration_log ORDER BY created_at DESC")
        
        logs = cursor.fetchall()
        
        # Transform field names for frontend compatibility
        result = []
        for log in logs:
            result.append({
                "id": log['log_id'],
                "gateway_code": log['gateway_code'],
                "action": log['action'],
                "status": log['action'].lower(),
                "performed_by": log['performed_by'],
                "remarks": log['remarks'],
                "created_at": log['created_at'].isoformat() if log.get('created_at') else None
            })
        
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.post("/api/registration-approvals")
async def create_registration_approval(request: Any = Body(...)):
    """Create registration approval (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    if request is None:
        raise HTTPException(status_code=400, detail="Request body is required")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        gateway_code = request.get('gateway_code', '')
        action = request.get('action', 'SUBMITTED')
        performed_by = request.get('performed_by', 'system')
        remarks = request.get('remarks', '')
        
        query = """
        INSERT INTO registration_log (gateway_code, action, performed_by, remarks)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (gateway_code, action, performed_by, remarks))
        connection.commit()
        
        return {"status": "success", "message": "Approval created", "id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/registration-approvals/{approval_id}")
async def get_registration_approval(approval_id: int):
    """Get specific registration approval (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM registration_log WHERE log_id = %s", (approval_id,))
        log = cursor.fetchone()
        
        if not log:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        # Transform field names for frontend compatibility
        return {
            "id": log['log_id'],
            "gateway_code": log['gateway_code'],
            "action": log['action'],
            "status": log['action'].lower(),
            "performed_by": log['performed_by'],
            "remarks": log['remarks'],
            "created_at": log['created_at'].isoformat() if log.get('created_at') else None
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/api/registration-approvals/{approval_id}")
async def update_registration_approval(approval_id: int, request: Any = Body(...)):
    """Update registration approval (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    if request is None:
        raise HTTPException(status_code=400, detail="Request body is required")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        action = request.get('action', 'SUBMITTED')
        performed_by = request.get('performed_by', 'system')
        remarks = request.get('remarks', '')
        
        query = """
        UPDATE registration_log 
        SET action=%s, performed_by=%s, remarks=%s
        WHERE log_id=%s
        """
        cursor.execute(query, (action, performed_by, remarks, approval_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        connection.commit()
        return {"status": "success", "message": "Approval updated"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.delete("/api/registration-approvals/{approval_id}")
async def delete_registration_approval(approval_id: int):
    """Delete registration approval (frontend compatible endpoint)"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM registration_log WHERE log_id = %s", (approval_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        connection.commit()
        return {"status": "success", "message": "Approval deleted"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== AUDIT TABLES CRUD ====================

# ==================== TABLE 11: PERFORMANCE_LOGS ====================

@app.post("/api/audit/performance-logs")
async def add_performance_log(log: PerformanceLog):
    """Log system performance metrics"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO performance_logs 
        (server_type, server_id, cpu_usage_percent, memory_usage_percent, total_memory_mb, 
         used_memory_mb, disk_total_gb, disk_used_gb, disk_free_gb, active_connections, 
         request_per_second, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.server_type, log.server_id, log.cpu_usage_percent, log.memory_usage_percent,
            log.total_memory_mb, log.used_memory_mb, log.disk_total_gb, log.disk_used_gb,
            log.disk_free_gb, log.active_connections, log.request_per_second, log.status
        ))
        connection.commit()
        return {"status": "success", "message": "Performance log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/performance-logs")
async def get_performance_logs(status: Optional[str] = None, limit: int = 100):
    """Get performance logs"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if status:
            cursor.execute(
                "SELECT * FROM performance_logs WHERE status = %s ORDER BY id DESC LIMIT %s",
                (status, limit)
            )
        else:
            cursor.execute("SELECT * FROM performance_logs ORDER BY id DESC LIMIT %s", (limit,))
        
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('timestamp'):
                log['timestamp'] = log['timestamp'].isoformat()
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 12: ADMINISTRATION_LOGS ====================

@app.post("/api/audit/administration-logs")
async def add_administration_log(log: AdministrationLog):
    """Log administrative actions"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO administration_logs 
        (server_type, server_id, action_type, performed_by, target_entity, previous_value, 
         new_value, status, error_message, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.server_type, log.server_id, log.action_type, log.performed_by, log.target_entity,
            log.previous_value, log.new_value, log.status, log.error_message, log.ip_address
        ))
        connection.commit()
        return {"status": "success", "message": "Administration log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/administration-logs")
async def get_administration_logs(action_type: Optional[str] = None, status: Optional[str] = None, limit: int = 100):
    """Get administration logs"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM administration_logs WHERE 1=1"
        params = []
        
        if action_type:
            query += " AND action_type = %s"
            params.append(action_type)
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY id DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('timestamp'):
                log['timestamp'] = log['timestamp'].isoformat()
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 13: TRANSACTIONAL_LOGS ====================

@app.post("/api/audit/transactional-logs")
async def add_transactional_log(log: TransactionalLog):
    """Log transaction/service usage"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO transactional_logs 
        (request_id, client_subsystem, provider_subsystem, client_server_id, provider_server_id,
         service_code, service_version, request_time, response_time, duration_ms, response_status,
         http_status_code, request_size_bytes, response_size_bytes, correlation_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.request_id, log.client_subsystem, log.provider_subsystem, log.client_server_id,
            log.provider_server_id, log.service_code, log.service_version, log.request_time,
            log.response_time, log.duration_ms, log.response_status, log.http_status_code,
            log.request_size_bytes, log.response_size_bytes, log.correlation_id
        ))
        connection.commit()
        return {"status": "success", "message": "Transaction log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/transactional-logs")
async def get_transactional_logs(response_status: Optional[str] = None, service_code: Optional[str] = None, limit: int = 100):
    """Get transactional logs"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM transactional_logs WHERE 1=1"
        params = []
        
        if response_status:
            query += " AND response_status = %s"
            params.append(response_status)
        if service_code:
            query += " AND service_code = %s"
            params.append(service_code)
        
        query += " ORDER BY id DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('request_time'):
                log['request_time'] = log['request_time'].isoformat() if log['request_time'] else None
            if log.get('response_time'):
                log['response_time'] = log['response_time'].isoformat() if log['response_time'] else None
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TABLE 14: SECURITY_LOGS ====================

@app.post("/api/audit/security-logs")
async def add_security_log(log: SecurityLog):
    """Log security event"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO security_logs 
        (server_type, server_id, event_type, severity, user_id, subsystem, resource, action,
         status, failure_reason, ip_address, geo_location, certificate_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.server_type, log.server_id, log.event_type, log.severity, log.user_id,
            log.subsystem, log.resource, log.action, log.status, log.failure_reason,
            log.ip_address, log.geo_location, log.certificate_id
        ))
        connection.commit()
        return {"status": "success", "message": "Security log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== AUDIT TABLES CRUD ====================

# ==================== PERFORMANCE LOGS ====================

@app.post("/api/audit/performance-logs")
async def log_performance(log: PerformanceLog):
    """Log system performance metrics"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO performance_logs 
        (server_type, server_id, cpu_usage_percent, memory_usage_percent, total_memory_mb, 
         used_memory_mb, disk_total_gb, disk_used_gb, disk_free_gb, active_connections, 
         request_per_second, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.server_type, log.server_id, log.cpu_usage_percent, log.memory_usage_percent,
            log.total_memory_mb, log.used_memory_mb, log.disk_total_gb, log.disk_used_gb,
            log.disk_free_gb, log.active_connections, log.request_per_second, log.status
        ))
        connection.commit()
        return {"status": "success", "message": "Performance log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/performance-logs")
async def get_performance_logs(server_id: Optional[str] = None, limit: int = 100):
    """Get performance logs"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if server_id:
            cursor.execute(
                "SELECT * FROM performance_logs WHERE server_id = %s ORDER BY recorded_at DESC LIMIT %s",
                (server_id, limit)
            )
        else:
            cursor.execute("SELECT * FROM performance_logs ORDER BY recorded_at DESC LIMIT %s", (limit,))
        
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('recorded_at'):
                log['recorded_at'] = log['recorded_at'].isoformat()
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== ADMINISTRATION LOGS ====================

@app.post("/api/audit/administration-logs")
async def log_administration(log: AdministrationLog):
    """Log administrative actions"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO administration_logs 
        (server_type, server_id, action_type, performed_by, target_entity, previous_value, 
         new_value, status, error_message, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.server_type, log.server_id, log.action_type, log.performed_by, log.target_entity,
            log.previous_value, log.new_value, log.status, log.error_message, 
            log.ip_address, log.user_agent
        ))
        connection.commit()
        return {"status": "success", "message": "Administration log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/administration-logs")
async def get_administration_logs(action_type: Optional[str] = None, server_id: Optional[str] = None, limit: int = 100):
    """Get administration logs"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM administration_logs WHERE 1=1"
        params = []
        
        if action_type:
            query += " AND action_type = %s"
            params.append(action_type)
        if server_id:
            query += " AND server_id = %s"
            params.append(server_id)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('created_at'):
                log['created_at'] = log['created_at'].isoformat()
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== TRANSACTIONAL LOGS ====================

@app.post("/api/audit/transactional-logs")
async def log_transactional(log: TransactionalLog):
    """Log transaction/service usage"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO transactional_logs 
        (request_id, client_subsystem, provider_subsystem, client_server_id, provider_server_id,
         service_code, service_version, request_time, response_time, duration_ms,
         response_status, http_status_code, request_size_bytes, response_size_bytes, correlation_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.request_id, log.client_subsystem, log.provider_subsystem,
            log.client_server_id, log.provider_server_id, log.service_code,
            log.service_version, log.request_time, log.response_time, log.duration_ms,
            log.response_status, log.http_status_code, log.request_size_bytes,
            log.response_size_bytes, log.correlation_id
        ))
        connection.commit()
        return {"status": "success", "message": "Transaction log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/transactional-logs")
async def get_transactional_logs(status: Optional[str] = None, client: Optional[str] = None, provider: Optional[str] = None, limit: int = 100):
    """Get transactional logs"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM transactional_logs WHERE 1=1"
        params = []
        
        if status:
            query += " AND response_status = %s"
            params.append(status)
        if client:
            query += " AND client_subsystem = %s"
            params.append(client)
        if provider:
            query += " AND provider_subsystem = %s"
            params.append(provider)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('created_at'):
                log['created_at'] = log['created_at'].isoformat()
            if log.get('request_time'):
                log['request_time'] = log['request_time'].isoformat()
            if log.get('response_time'):
                log['response_time'] = log['response_time'].isoformat()
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== SECURITY LOGS ====================

@app.post("/api/audit/security-logs")
async def log_security(log: SecurityLog):
    """Log security event"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO security_logs 
        (server_type, server_id, event_type, severity, user_id, subsystem, resource, action,
         status, failure_reason, ip_address, geo_location, certificate_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            log.server_type, log.server_id, log.event_type, log.severity, log.user_id,
            log.subsystem, log.resource, log.action, log.status, log.failure_reason,
            log.ip_address, log.geo_location, log.certificate_id
        ))
        connection.commit()
        return {"status": "success", "message": "Security log recorded", "log_id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/security-logs")
async def get_security_logs(severity: Optional[str] = None, event_type: Optional[str] = None, 
                            server_id: Optional[str] = None, limit: int = 100):
    """Get security logs"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM security_logs WHERE 1=1"
        params = []
        
        if severity:
            query += " AND severity = %s"
            params.append(severity)
        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)
        if server_id:
            query += " AND server_id = %s"
            params.append(server_id)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        for log in logs:
            if log.get('created_at'):
                log['created_at'] = log['created_at'].isoformat()
        
        return {"status": "success", "total": len(logs), "logs": logs}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/api/audit/security-logs/summary")
async def get_security_summary():
    """Get security logs summary"""
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get summary by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count FROM security_logs 
            GROUP BY severity ORDER BY severity
        """)
        severity_summary = cursor.fetchall()
        
        # Get summary by event type
        cursor.execute("""
            SELECT event_type, COUNT(*) as count FROM security_logs 
            GROUP BY event_type ORDER BY event_type
        """)
        event_summary = cursor.fetchall()
        
        # Get today's stats
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as success,
                   SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
            FROM security_logs 
            WHERE DATE(created_at) = CURDATE()
        """)
        today_stats = cursor.fetchone()
        
        return {
            "status": "success",
            "severity_summary": severity_summary,
            "event_summary": event_summary,
            "today_stats": today_stats
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
