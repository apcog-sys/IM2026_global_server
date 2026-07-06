from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector
from mysql.connector import Error

from datetime import datetime
import uvicorn
import os

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

class EntityResponse(Entity):
    entity_id: int


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


@app.post("/api/init-db")
async def init_db():
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        # 1. ENTITIES table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id INT AUTO_INCREMENT PRIMARY KEY,
            entity_code VARCHAR(100) UNIQUE NOT NULL,
            entity_name VARCHAR(255) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 2. NETWORK_CONFIG table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_config (
            id INT AUTO_INCREMENT PRIMARY KEY,
            gateway_code VARCHAR(100) UNIQUE NOT NULL,
            entity_id INT NOT NULL,
            title VARCHAR(255),
            version VARCHAR(50),
            network_instance VARCHAR(50),
            host VARCHAR(100),
            port INT,
            hostname VARCHAR(255),
            ip_address VARCHAR(50),
            environment VARCHAR(50),
            status VARCHAR(50) DEFAULT 'PENDING',
            auth_cert_id INT,
            sign_cert_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE
        )
        """)

        # 3. SERVER_KEYS table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_keys (
            key_id INT AUTO_INCREMENT PRIMARY KEY,
            gateway_code VARCHAR(100) NOT NULL,
            key_type VARCHAR(20) NOT NULL,
            public_key LONGTEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code) ON DELETE CASCADE,
            UNIQUE KEY unique_key (gateway_code, key_type)
        )
        """)

        # 4. CERTIFICATE_REQUESTS table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificate_requests (
            csr_id INT AUTO_INCREMENT PRIMARY KEY,
            gateway_code VARCHAR(100) NOT NULL,
            key_id INT NOT NULL,
            csr_data LONGTEXT NOT NULL,
            cert_type VARCHAR(20) NOT NULL,
            status VARCHAR(50) DEFAULT 'PENDING',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code) ON DELETE CASCADE,
            FOREIGN KEY (key_id) REFERENCES server_keys(key_id) ON DELETE CASCADE
        )
        """)

        # 5. CERTIFICATES table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            cert_id INT AUTO_INCREMENT PRIMARY KEY,
            gateway_code VARCHAR(100) NOT NULL,
            key_id INT NOT NULL,
            cert_type VARCHAR(20) NOT NULL,
            certificate LONGTEXT NOT NULL,
            issued_by VARCHAR(255),
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            status VARCHAR(50) DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code) ON DELETE CASCADE,
            FOREIGN KEY (key_id) REFERENCES server_keys(key_id) ON DELETE CASCADE
        )
        """)

        # 6. REGISTRATION_LOG table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registration_log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            gateway_code VARCHAR(100) NOT NULL,
            action VARCHAR(50) NOT NULL,
            performed_by VARCHAR(255),
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code) ON DELETE CASCADE
        )
        """)

        # 7. GLOBAL_DIRECTORY table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_directory (
            directory_id INT AUTO_INCREMENT PRIMARY KEY,
            entity_code VARCHAR(100) NOT NULL,
            gateway_code VARCHAR(100) UNIQUE NOT NULL,
            service_url VARCHAR(255),
            auth_cert_id INT,
            sign_cert_id INT,
            status VARCHAR(50) DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code) ON DELETE CASCADE,
            FOREIGN KEY (auth_cert_id) REFERENCES certificates(cert_id),
            FOREIGN KEY (sign_cert_id) REFERENCES certificates(cert_id)
        )
        """)

        connection.commit()
        return {"status": "success", "message": "Database tables initialized successfully"}

    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


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
        INSERT INTO entities (entity_code, entity_name, entity_type, status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (entity.entity_code, entity.entity_name, entity.entity_type, entity.status))
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
        SET entity_code=%s, entity_name=%s, entity_type=%s, status=%s
        WHERE entity_id=%s
        """
        cursor.execute(query, (
            entity_update.entity_code,
            entity_update.entity_name,
            entity_update.entity_type,
            entity_update.status,
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


# ==================== TABLE 2: NETWORK_CONFIG CRUD ====================

@app.post("/api/network-config")
async def create_network_config(config: NetworkConfig):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO network_config 
        (gateway_code, entity_id, title, version, network_instance, host, port, hostname, ip_address, environment, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
        """
        cursor.execute(query, (
            config.gateway_code, config.entity_id, config.title, config.version,
            config.network_instance, config.host, config.port, config.hostname,
            config.ip_address, config.environment
        ))
        connection.commit()
        
        # Auto-log SUBMITTED event
        log_query = """
        INSERT INTO registration_log (gateway_code, action, performed_by)
        VALUES (%s, 'SUBMITTED', 'security_server')
        """
        cursor.execute(log_query, (config.gateway_code,))
        connection.commit()
        
        return {"status": "success", "message": "Gateway registered (PENDING)", "id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


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
        
        return {"status": "success", "total": len(configs), "configs": configs}
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
        
        return {"status": "success", "total": len(csrs), "csrs": csrs}
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
        
        return {"status": "success", "csr": csr}
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


# ==================== TABLE 5: CERTIFICATES CRUD ====================

@app.post("/api/certificates")
async def create_certificate(cert: Certificate):
    if not db_config:
        raise HTTPException(status_code=400, detail="Database not configured")
    
    connection = None
    try:
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        
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
        
        return {"status": "success", "message": f"{cert.cert_type} certificate stored (ACTIVE)", "cert_id": cert_id}
    except Error as e:
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
        
        # Auto-update network_config status based on action
        if log.action == "APPROVED":
            cursor.execute(
                "UPDATE network_config SET status = 'APPROVED' WHERE gateway_code = %s",
                (log.gateway_code,)
            )
        elif log.action == "REJECTED":
            cursor.execute(
                "UPDATE network_config SET status = 'REJECTED' WHERE gateway_code = %s",
                (log.gateway_code,)
            )
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
        
        # Check if gateway is APPROVED
        check_query = "SELECT status FROM network_config WHERE gateway_code = %s"
        cursor.execute(check_query, (entry.gateway_code,))
        result = cursor.fetchone()
        
        if not result or result[0] != "APPROVED":
            raise HTTPException(status_code=400, detail="Gateway must be APPROVED before publishing to directory")
        
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
        
        if status:
            query = """
            SELECT gd.*, e.entity_name, nc.host, nc.port, nc.hostname
            FROM global_directory gd
            JOIN entities e ON gd.entity_code = e.entity_code
            JOIN network_config nc ON gd.gateway_code = nc.gateway_code
            WHERE gd.status = %s
            ORDER BY gd.created_at DESC
            """
            cursor.execute(query, (status,))
        else:
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


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "db_configured": db_config is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def serve_index():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return {"message": "Welcome to Global Server v2.0 - Full CRUD for all 7 tables"}


# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
