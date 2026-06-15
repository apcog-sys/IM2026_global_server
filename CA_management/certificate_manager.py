"""
Certificate Management System
Integrates Certificate Authority with service endpoints
Handles:
  - Certificate request workflow
  - Authentication + Signature certificate generation
  - Certificate chain management
  - MySQL storage
"""

import json
from datetime import datetime
from uuid import uuid4
import logging
from pathlib import Path

import mysql.connector
from pydantic import BaseModel, Field

from .ca_authority import get_certificate_authority, CertificateAuthority

logger = logging.getLogger(__name__)


class CertificateRequestModel(BaseModel):
    """Model for certificate request"""
    server_id: str
    server_name: str
    organization: str
    public_key_pem: str
    address: str = Field(default="localhost", description="Server address for AUTH certs")
    certificate_type: str = Field(default="auth", description="auth or sign")
    network_instance: str = Field(default="EE")


class CSRSigningModel(BaseModel):
    """Model for CSR signing request"""
    csr_pem: str
    server_id: str
    cert_type: str = Field(default="auth", description="auth or sign")


class CertificateResponseModel(BaseModel):
    certificate_id: str
    server_id: str
    certificate_type: str
    certificate_pem: str
    issued_date: str
    expiry_date: str
    thumbprint: str
    message: str


class CertificateManager:
    """
    Manages certificate lifecycle:
    1. Request → certificate submission
    2. Generate → CA signs (Authentication + Signature)
    3. Store → MySQL + Filesystem
    4. Distribute → Service endpoints
    """

    def __init__(self, config: dict = None, db_config: dict = None):
        """
        Initialize certificate manager
        
        Args:
            config: Server configuration
            db_config: MySQL connection config
        """
        self.config = config or {}
        self.db_config = db_config or {}
        self.ca = get_certificate_authority(config=config)
        
        logger.info("[CERT-MGR] Certificate Manager initialized")

    def _get_db_connection(self):
        """Create MySQL connection"""
        try:
            conn = mysql.connector.connect(
                host=self.db_config.get("host", "localhost"),
                user=self.db_config.get("user", "root"),
                password=self.db_config.get("password", ""),
                database=self.db_config.get("database", "service_gateway")
            )
            return conn
        except mysql.connector.Error as err:
            logger.error(f"[CERT-MGR] Database connection error: {err}")
            raise

    def _calculate_thumbprint(self, certificate_pem: str) -> str:
        """Calculate SHA-256 thumbprint of certificate"""
        import hashlib
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        
        cert = x509.load_pem_x509_certificate(
            certificate_pem.encode() if isinstance(certificate_pem, str) else certificate_pem,
            default_backend()
        )
        
        thumbprint = hashlib.sha256(
            cert.public_bytes(serialization.Encoding.DER)
        ).hexdigest()
        
        return thumbprint

    def _store_certificate(self, cert_id: str, server_id: str, cert_type: str,
                          certificate_pem: str, cert_path: str, 
                          issued_date: str, expiry_date: str):
        """Store certificate in MySQL database"""
        conn = None
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Calculate thumbprint
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            import hashlib
            
            cert = x509.load_pem_x509_certificate(
                certificate_pem.encode() if isinstance(certificate_pem, str) else certificate_pem,
                default_backend()
            )
            
            thumbprint = hashlib.sha256(
                cert.public_bytes(serialization.Encoding.DER)
            ).hexdigest()
            
            query = """
            INSERT INTO security_server_certificates 
            (certificate_id, server_id, certificate_type, thumbprint, 
             certificate_path, issued_date, expiry_date, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (cert_id, server_id, cert_type, thumbprint, 
                     cert_path, issued_date, expiry_date, "ACTIVE")
            
            cursor.execute(query, values)
            conn.commit()
            
            logger.info(f"[CERT-MGR] Certificate stored in database: {cert_id}")
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error storing certificate: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()

    def generate_auth_certificate(self, request: CertificateRequestModel) -> CertificateResponseModel:
        """Generate Authentication certificate"""
        try:
            logger.info(f"[CERT-MGR] Generating Authentication certificate for {request.server_id}")
            
            # Generate certificate from CA
            cert_pem, cert_path = self.ca.generate_auth_certificate(
                server_id=request.server_id,
                server_name=request.server_name,
                address=request.address,
                organization=request.organization,
                public_key_pem=request.public_key_pem
            )
            
            # Extract certificate dates
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            
            cert = x509.load_pem_x509_certificate(
                cert_pem.encode() if isinstance(cert_pem, str) else cert_pem,
                default_backend()
            )
            
            issued_date = cert.not_valid_before_utc.isoformat()
            expiry_date = cert.not_valid_after_utc.isoformat()
            
            # Calculate thumbprint
            from cryptography.hazmat.primitives import serialization
            import hashlib
            
            thumbprint = hashlib.sha256(
                cert.public_bytes(serialization.Encoding.DER)
            ).hexdigest()
            
            # Store in database
            cert_id = str(uuid4())
            self._store_certificate(
                cert_id=cert_id,
                server_id=request.server_id,
                cert_type="auth",
                certificate_pem=cert_pem,
                cert_path=cert_path,
                issued_date=issued_date,
                expiry_date=expiry_date
            )
            
            return CertificateResponseModel(
                status="success",
                certificate_id=cert_id,
                server_id=request.server_id,
                certificate_type="auth",
                certificate_pem=cert_pem,
                issued_date=issued_date,
                expiry_date=expiry_date,
                thumbprint=thumbprint,
                message="Authentication certificate generated successfully"
            )
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error generating Authentication certificate: {e}")
            raise

    def generate_sign_certificate(self, request: CertificateRequestModel) -> CertificateResponseModel:
        """Generate Signature certificate"""
        try:
            logger.info(f"[CERT-MGR] Generating Signature certificate for {request.server_id}")
            
            # Generate certificate from CA
            cert_pem, cert_path = self.ca.generate_sign_certificate(
                server_id=request.server_id,
                server_name=request.server_name,
                organization=request.organization,
                public_key_pem=request.public_key_pem
            )
            
            # Extract certificate dates
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            import hashlib
            
            cert = x509.load_pem_x509_certificate(
                cert_pem.encode() if isinstance(cert_pem, str) else cert_pem,
                default_backend()
            )
            
            issued_date = cert.not_valid_before.isoformat()
            expiry_date = cert.not_valid_after.isoformat()
            
            # Calculate thumbprint
            thumbprint = hashlib.sha256(
                cert.public_bytes(serialization.Encoding.DER)
            ).hexdigest()
            
            # Store in database
            cert_id = str(uuid4())
            self._store_certificate(
                cert_id=cert_id,
                server_id=request.server_id,
                cert_type="sign",
                certificate_pem=cert_pem,
                cert_path=cert_path,
                issued_date=issued_date,
                expiry_date=expiry_date
            )
            
            return CertificateResponseModel(
                status="success",
                certificate_id=cert_id,
                server_id=request.server_id,
                certificate_type="sign",
                certificate_pem=cert_pem,
                issued_date=issued_date,
                expiry_date=expiry_date,
                thumbprint=thumbprint,
                message="Signature certificate generated successfully"
            )
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error generating Signature certificate: {e}")
            raise

    def generate_both_certificates(self, request: CertificateRequestModel) -> dict:
        """Generate both Authentication and Signature certificates"""
        try:
            logger.info(f"[CERT-MGR] Generating both certificates for {request.server_id}")
            
            # Generate Authentication certificate
            request.certificate_type = "auth"
            auth_response = self.generate_auth_certificate(request)
            
            # Generate Signature certificate
            request.certificate_type = "sign"
            sign_response = self.generate_sign_certificate(request)
            
            return {
                "status": "success",
                "auth_certificate": auth_response.dict(),
                "sign_certificate": sign_response.dict()
            }
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error generating both certificates: {e}")
            raise

    def sign_csr(self, csr_pem: str, server_id: str, cert_type: str = "auth") -> CertificateResponseModel:
        """
        Sign a Certificate Signing Request (CSR) and return signed certificate
        
        Args:
            csr_pem: CSR in PEM format
            server_id: Security Server ID
            cert_type: "auth" or "sign"
            
        Returns:
            CertificateResponseModel with signed certificate
        """
        try:
            # Sanitize inputs
            server_id = str(server_id).strip()
            cert_type = str(cert_type).strip()
            
            # Validate cert_type
            if cert_type.lower() not in ["auth", "sign"]:
                raise ValueError(f"cert_type must be 'auth' or 'sign', got: {cert_type}")
            
            # Validate CSR is not empty
            if not csr_pem or not csr_pem.strip():
                raise ValueError("csr_pem cannot be empty")
            
            logger.info(f"[CERT-MGR] Signing CSR for {server_id} (type: {cert_type})")
            logger.info(f"[CERT-MGR] CSR length: {len(csr_pem)} characters")
            
            # Sign CSR using CA
            cert_pem, cert_path = self.ca.sign_csr(
                csr_pem=csr_pem,
                server_id=server_id,
                cert_type=cert_type
            )
            
            # Extract certificate information
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            import hashlib
            
            cert = x509.load_pem_x509_certificate(
                cert_pem.encode() if isinstance(cert_pem, str) else cert_pem,
                default_backend()
            )
            
            issued_date = cert.not_valid_before_utc.isoformat()
            expiry_date = cert.not_valid_after_utc.isoformat()
            
            # Calculate thumbprint
            thumbprint = hashlib.sha256(
                cert.public_bytes(serialization.Encoding.DER)
            ).hexdigest()
            
            logger.info(f"[CERT-MGR] ✅ CSR signed successfully for {server_id}")
            
            return CertificateResponseModel(
                status="success",
                certificate_id=str(uuid4()),
                server_id=server_id,
                certificate_type=cert_type,
                certificate_pem=cert_pem,
                issued_date=issued_date,
                expiry_date=expiry_date,
                thumbprint=thumbprint,
                message=f"CSR signed successfully ({cert_type} certificate)"
            )
            
        except ValueError as ve:
            logger.error(f"[CERT-MGR] Validation error signing CSR: {ve}")
            raise
        except Exception as e:
            logger.error(f"[CERT-MGR] Error signing CSR: {e}")
            raise

    def get_certificate_by_id(self, cert_id: str) -> dict:
        """Get certificate details by ID"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM security_server_certificates WHERE certificate_id = %s"
            cursor.execute(query, (cert_id,))
            result = cursor.fetchone()
            
            return result or {"error": "Certificate not found"}
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error retrieving certificate: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_certificates_by_server(self, server_id: str) -> list:
        """Get all certificates for a server"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM security_server_certificates WHERE server_id = %s ORDER BY created_at DESC"
            cursor.execute(query, (server_id,))
            results = cursor.fetchall()
            
            return results or []
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error retrieving server certificates: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_ca_root_certificate(self) -> dict:
        """Get CA root certificate"""
        try:
            ca_cert_pem = self.ca.get_ca_certificate()
            
            return {
                "status": "success",
                "certificate_type": "root_ca",
                "certificate_pem": ca_cert_pem
            }
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error retrieving CA root certificate: {e}")
            raise

    def export_certificate_bundle(self, server_id: str) -> str:
        """Export complete certificate bundle"""
        try:
            bundle_path = self.ca.export_certificate_bundle(server_id)
            return bundle_path
            
        except Exception as e:
            logger.error(f"[CERT-MGR] Error exporting certificate bundle: {e}")
            raise


# Global certificate manager instance
_certificate_manager_instance = None


def get_certificate_manager(config: dict = None, db_config: dict = None) -> CertificateManager:
    """Get or create global Certificate Manager instance"""
    global _certificate_manager_instance
    if _certificate_manager_instance is None:
        _certificate_manager_instance = CertificateManager(config=config, db_config=db_config)
    return _certificate_manager_instance
