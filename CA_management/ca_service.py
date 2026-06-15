"""
CA Service - Independent FastAPI Service for Certificate Management
Runs on port 9002 (separate from main security server on 9001)

Endpoints:
  POST /api/certificates/sign-csr            - Sign a Certificate Signing Request (CSR)
  POST /api/certificates/generate-auth        - Generate Authentication certificate
  POST /api/certificates/generate-sign        - Generate Signature certificate
  POST /api/certificates/generate-both        - Generate both certificates
  GET  /api/certificates/ca-root              - Download CA root certificate
  GET  /api/certificates/{server_id}/chain    - Get certificate chain
  GET  /api/certificates/{cert_id}            - Get certificate details
  GET  /api/certificates/server/{server_id}   - Get all certificates for server
  GET  /health                                - Health check
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from CA_management.certificate_manager import (
    CertificateManager,
    CertificateRequestModel,
    CSRSigningModel,
    get_certificate_manager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Certificate Authority Service",
    description="Public Key Infrastructure (PKI) Certificate Management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "gs1"
}

# Certificate manager
cert_manager = None


@app.on_event("startup")
async def startup_event():
    """Initialize certificate manager on startup"""
    global cert_manager
    try:
        cert_manager = get_certificate_manager(config={}, db_config=DB_CONFIG)
        logger.info("[CA-SERVICE] Certificate Manager initialized successfully")
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error initializing Certificate Manager: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Certificate Authority",
        "version": "1.0.0",
        "port": 9002
    }


@app.post("/api/certificates/generate-auth")
async def generate_auth_certificate(request: CertificateRequestModel):
    """
    Generate Authentication certificate for TLS/HTTPS
    
    Request body:
    {
        "server_id": "SECURITY_SERVER_1",
        "server_name": "Primary Gateway",
        "organization": "My Organization",
        "address": "10.0.0.50",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    }
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        logger.info(f"[CA-SERVICE] Generating Authentication certificate for {request.server_id}")
        
        response = cert_manager.generate_auth_certificate(request)
        
        return JSONResponse(
            status_code=201,
            content=response.dict()
        )
        
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in generate_auth_certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/certificates/generate-sign")
async def generate_sign_certificate(request: CertificateRequestModel):
    """
    Generate Signature certificate for message signing
    
    Request body:
    {
        "server_id": "SECURITY_SERVER_1",
        "server_name": "Primary Gateway",
        "organization": "My Organization",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    }
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        logger.info(f"[CA-SERVICE] Generating Signature certificate for {request.server_id}")
        
        response = cert_manager.generate_sign_certificate(request)
        
        return JSONResponse(
            status_code=201,
            content=response.dict()
        )
        
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in generate_sign_certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/certificates/generate-both")
async def generate_both_certificates(request: CertificateRequestModel):
    """
    Generate both Authentication and Signature certificates in one call
    
    Request body:
    {
        "server_id": "SECURITY_SERVER_1",
        "server_name": "Primary Gateway",
        "organization": "My Organization",
        "address": "10.0.0.50",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
    }
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        logger.info(f"[CA-SERVICE] Generating both certificates for {request.server_id}")
        
        response = cert_manager.generate_both_certificates(request)
        
        return JSONResponse(
            status_code=201,
            content=response
        )
        
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in generate_both_certificates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/certificates/sign-csr")
async def sign_csr(request: CSRSigningModel):
    """
    Sign a Certificate Signing Request (CSR) and return signed certificate
    
    Request body:
    {
        "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
        "server_id": "SECURITY_SERVER_1",
        "cert_type": "auth"  # or "sign"
    }
    
    Returns:
    {
        "status": "success",
        "certificate_pem": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
        "issued_date": "2026-04-15T10:30:00",
        "expiry_date": "2027-04-15T10:30:00",
        "certificate_id": "uuid",
        "message": "CSR signed successfully"
    }
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        # Sanitize inputs
        server_id = str(request.server_id).strip()
        cert_type = str(request.cert_type).strip()
        
        logger.info(f"[CA-SERVICE] Signing CSR for {server_id} (type: {cert_type})")
        
        response = cert_manager.sign_csr(
            csr_pem=request.csr_pem,
            server_id=server_id,
            cert_type=cert_type
        )
        
        return JSONResponse(
            status_code=201,
            content=response.dict()
        )
        
    except ValueError as ve:
        logger.error(f"[CA-SERVICE] Validation error in sign_csr: {ve}")
        raise HTTPException(status_code=400, detail=f"Invalid CSR: {str(ve)}")
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in sign_csr: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificates/ca-root")
async def get_ca_root():
    """
    Get CA root certificate (self-signed)
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        logger.info("[CA-SERVICE] Retrieving CA root certificate")
        
        response = cert_manager.get_ca_root_certificate()
        
        return JSONResponse(
            status_code=200,
            content=response
        )
        
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in get_ca_root: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificates/{server_id}/chain")
async def get_certificate_chain(server_id: str):
    """
    Get complete certificate chain for a server
    Includes: Root CA + Authentication certificate + Signature certificate
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        logger.info(f"[CA-SERVICE] Retrieving certificate chain for {server_id}")
        
        # Get chain from CA
        chain = cert_manager.ca.get_certificate_chain(server_id)
        
        # Get CA root
        ca_root = cert_manager.get_ca_root_certificate()
        
        # Get all certificates for server
        certs = cert_manager.get_certificates_by_server(server_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "server_id": server_id,
                "chain": chain,
                "ca_root": ca_root,
                "certificates": certs,
                "message": "Certificate chain retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in get_certificate_chain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificates/{cert_id}")
async def get_certificate(cert_id: str):
    """
    Get certificate details by certificate ID
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        logger.info(f"[CA-SERVICE] Retrieving certificate: {cert_id}")
        
        cert = cert_manager.get_certificate_by_id(cert_id)
        
        if "error" in cert:
            raise HTTPException(status_code=404, detail=cert["error"])
        
        return JSONResponse(
            status_code=200,
            content=cert
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in get_certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificates/server/{server_id}")
async def get_server_certificates(server_id: str):
    """
    Get all certificates for a specific server
    """
    try:
        if not cert_manager:
            raise HTTPException(status_code=503, detail="Certificate Manager not initialized")
        
        logger.info(f"[CA-SERVICE] Retrieving all certificates for {server_id}")
        
        certs = cert_manager.get_certificates_by_server(server_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "server_id": server_id,
                "certificates": certs,
                "count": len(certs)
            }
        )
        
    except Exception as e:
        logger.error(f"[CA-SERVICE] Error in get_server_certificates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("[CA-SERVICE] Starting Certificate Authority Service on port 9002...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9002,
        log_level="info"
    )
