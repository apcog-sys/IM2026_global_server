# Dual CSR/CRT Registration Workflow - Complete Guide

## Overview

The security server registration system uses a **dual certificate approach**:
- **AUTH Certificate** (from auth.csr): For TLS/HTTPS connections
- **SIGN Certificate** (from sign.csr): For message signing and verification

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY SERVER REGISTRATION FLOW                     │
└─────────────────────────────────────────────────────────────────────────┘

    Security Server                 Global Server              CA Service
           │                              │                        │
           │  1. Generate CSRs locally    │                        │
           │     - auth.csr               │                        │
           │     - sign.csr               │                        │
           │                              │                        │
           │  2. Submit dual CSRs         │                        │
           ├─────────────────────────────>│                        │
           │                              │  3. Forward auth.csr   │
           │                              ├───────────────────────>│
           │                              │     Verify & Sign      │
           │                              │<───────────────────────┤
           │                              │     Return auth.crt    │
           │                              │                        │
           │                              │  4. Forward sign.csr   │
           │                              ├───────────────────────>│
           │                              │     Verify & Sign      │
           │                              │<───────────────────────┤
           │                              │     Return sign.crt    │
           │                              │                        │
           │  5. Get both .crt files     │                        │
           │<─────────────────────────────┤                        │
           │     + metadata               │                        │
           │                              │                        │
           │  6. Register with CA-        │                        │
           │     verified certs           │                        │
           ├─────────────────────────────>│                        │
           │                              │ Store in DB:           │
           │                              │ - auth.csr + auth.crt  │
           │                              │ - sign.csr + sign.crt  │
           │                              │ - Metadata             │
           │                              │                        │
           │  7. Get both .crt files     │                        │
           │     for local storage        │                        │
           │<─────────────────────────────┤                        │
           │                              │                        │
           │  8. Save files locally:      │                        │
           │     - SS_1_auth.crt          │                        │
           │     - SS_1_sign.crt          │                        │
           │     - registration.metadata  │                        │
           │                              │                        │
           ▼                              ▼                        ▼
```

---

## Step-by-Step Workflow

### Step 1: Generate Dual CSRs (Security Server - Local)

The security server generates TWO separate CSR files locally:

```bash
#!/bin/bash

# ========== GENERATE KEY PAIRS ==========
openssl genrsa -out server_auth.key 2048
openssl genrsa -out server_sign.key 2048

# ========== AUTH CSR CONFIG ==========
cat > auth_csr.conf << 'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization Name
CN = SECURITY_SERVER_1.auth

[v3_req]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = DNS:security-server-1.local, IP:10.0.0.50
EOF

# ========== SIGN CSR CONFIG ==========
cat > sign_csr.conf << 'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization Name
CN = SECURITY_SERVER_1.sign

[v3_req]
keyUsage = digitalSignature, nonRepudiation
extendedKeyUsage = emailProtection, codeSigning
EOF

# ========== GENERATE CSRs ==========
openssl req -new -key server_auth.key -out auth.csr -config auth_csr.conf
openssl req -new -key server_sign.key -out sign.csr -config sign_csr.conf

echo "✓ Generated: auth.csr and sign.csr"

# ========== CONVERT TO PEM FOR API ==========
AUTH_CSR=$(cat auth.csr | tr '\n' '\\n')
SIGN_CSR=$(cat sign.csr | tr '\n' '\\n')

echo "Ready to submit to Global Server"
```

### Step 2: Submit Dual CSRs to Global Server for CA Verification

**Endpoint**: `POST /api/security-servers/request-certificates`

**Request**:
```bash
curl -X POST http://localhost:9000/api/security-servers/request-certificates \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "SECURITY_SERVER_1",
    "server_name": "Primary Security Gateway",
    "organization": "My Organization",
    "auth_csr": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCVVMxEDAOBgNVBAgTB0dlb3JnaWExDjAM\n...\n-----END CERTIFICATE REQUEST-----",
    "sign_csr": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCVVMxEDAOBgNVBAgTB0dlb3JnaWExDjAM\n...\n-----END CERTIFICATE REQUEST-----",
    "address": "10.0.0.50",
    "network_instance": "EE"
  }'
```

**Response (Success - 200)**:
```json
{
  "status": "success",
  "message": "Both AUTH and SIGN certificates generated by CA",
  "auth_certificate": {
    "certificate_id": "cert-uuid-auth-12345",
    "certificate_type": "auth",
    "crt_file": "-----BEGIN CERTIFICATE-----\nMIIC9jCCAeYCCQCPHfIAKzRlLjANBgkqhkiG9w0BAQsFADA...\n-----END CERTIFICATE-----",
    "thumbprint": "SHA256:A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0",
    "expiry_date": "2027-04-09T10:30:00Z",
    "issued_date": "2026-04-09T10:30:00Z"
  },
  "sign_certificate": {
    "certificate_id": "cert-uuid-sign-67890",
    "certificate_type": "sign",
    "crt_file": "-----BEGIN CERTIFICATE-----\nMIIC9jCCAeYCCQCPHfIAKzRlLjANBgkqhkiG9w0BAQsFADA...\n-----END CERTIFICATE-----",
    "thumbprint": "SHA256:B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1",
    "expiry_date": "2027-04-09T10:30:00Z",
    "issued_date": "2026-04-09T10:30:00Z"
  },
  "next_step": "Submit both certificates to /api/security-servers/register",
  "metadata": {
    "server_id": "SECURITY_SERVER_1",
    "request_time": "2026-04-09T10:30:00Z",
    "status": "certificates_issued"
  }
}
```

---

### Step 3: Register Security Server with Verified Certificates

**Endpoint**: `POST /api/security-servers/register`

**Request**:
```bash
curl -X POST http://localhost:9000/api/security-servers/register \
  -H "Content-Type: application/json" \
  -d '{
    "registration_id": "REG_SS_001",
    "server_id": "SECURITY_SERVER_1",
    "server_name": "Primary Security Gateway",
    "organization": "My Organization",
    "address": "10.0.0.50",
    "port": 9001,
    "network_instance": "EE",
    
    "auth_csr": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
    "auth_crt": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "auth_certificate_id": "cert-uuid-auth-12345",
    "auth_thumbprint": "SHA256:A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0",
    "auth_expiry_date": "2027-04-09T10:30:00Z",
    
    "sign_csr": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
    "sign_crt": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "sign_certificate_id": "cert-uuid-sign-67890",
    "sign_thumbprint": "SHA256:B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1",
    "sign_expiry_date": "2027-04-09T10:30:00Z",
    
    "created_by": "admin@organization.com"
  }'
```

**Response (Success - 200)**:
```json
{
  "status": "success",
  "message": "Security server registered successfully with dual certificates",
  "registration": {
    "registration_id": "REG_SS_001",
    "server_id": "SECURITY_SERVER_1",
    "status": "registered",
    "registered_at": "2026-04-09T10:35:00Z"
  },
  "certificates": {
    "auth": {
      "certificate_id": "cert-uuid-auth-12345",
      "certificate_type": "auth",
      "thumbprint": "SHA256:A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0",
      "expiry_date": "2027-04-09T10:30:00Z"
    },
    "sign": {
      "certificate_id": "cert-uuid-sign-67890",
      "certificate_type": "sign",
      "thumbprint": "SHA256:B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1",
      "expiry_date": "2027-04-09T10:30:00Z"
    }
  },
  "crt_files": {
    "auth": {
      "filename": "SECURITY_SERVER_1_auth.crt",
      "content": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
      "instructions": "Save this AUTH (.crt) file in your security server's certificate directory for TLS/HTTPS"
    },
    "sign": {
      "filename": "SECURITY_SERVER_1_sign.crt",
      "content": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
      "instructions": "Save this SIGN (.crt) file in your security server's certificate directory for message signing"
    }
  },
  "metadata": {
    "filename": "SECURITY_SERVER_1_registration.metadata",
    "content": "REGISTRATION-ID: REG_SS_001\nSERVER-ID: SECURITY_SERVER_1\nSERVER-NAME: Primary Security Gateway\nORGANIZATION: My Organization\nADDRESS: 10.0.0.50\nPORT: 9001\nNETWORK-INSTANCE: EE\nREGISTERED-AT: 2026-04-09T10:35:00Z\nSTATUS: registered\n\n=== AUTH CERTIFICATE ===\nCERTIFICATE-TYPE: AUTH (Authentication/TLS)\nCERTIFICATE-ID: cert-uuid-auth-12345\nTHUMBPRINT: SHA256:A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0\nISSUED-DATE: 2026-04-09T10:35:00Z\nEXPIRY-DATE: 2027-04-09T10:30:00Z\nSTATUS: VERIFIED\n\n=== SIGN CERTIFICATE ===\nCERTIFICATE-TYPE: SIGN (Message Signing)\nCERTIFICATE-ID: cert-uuid-sign-67890\nTHUMBPRINT: SHA256:B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1\nISSUED-DATE: 2026-04-09T10:35:00Z\nEXPIRY-DATE: 2027-04-09T10:30:00Z\nSTATUS: VERIFIED"
  }
}
```

### Step 4: Save Files Locally

Security Server saves the returned files:

```bash
# Extract from Step 3 response and save locally
cat > SECURITY_SERVER_1_auth.crt << 'EOF'
[content from crt_files.auth.content]
EOF

cat > SECURITY_SERVER_1_sign.crt << 'EOF'
[content from crt_files.sign.content]
EOF

cat > SECURITY_SERVER_1_registration.metadata << 'EOF'
[content from metadata.content]
EOF

echo "✓ Saved certificates for TLS and message signing"
echo "  - SECURITY_SERVER_1_auth.crt (for HTTPS/TLS)"
echo "  - SECURITY_SERVER_1_sign.crt (for message signing)"
echo "  - SECURITY_SERVER_1_registration.metadata"
```

---

## Python Implementation Example

```python
import requests
import json
import subprocess
from pathlib import Path

def generate_dual_csrs(server_id="SECURITY_SERVER_1"):
    """Generate AUTH and SIGN CSRs"""
    
    # Generate keys
    subprocess.run(['openssl', 'genrsa', '-out', 'server_auth.key', '2048'], 
                   capture_output=True)
    subprocess.run(['openssl', 'genrsa', '-out', 'server_sign.key', '2048'], 
                   capture_output=True)
    
    # Create AUTH CSR config
    auth_conf = """[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization
CN = {}.auth

[v3_req]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
""".format(server_id)
    
    with open('auth_csr.conf', 'w') as f:
        f.write(auth_conf)
    
    # Create SIGN CSR config
    sign_conf = """[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization
CN = {}.sign

[v3_req]
keyUsage = digitalSignature, nonRepudiation
extendedKeyUsage = emailProtection, codeSigning
""".format(server_id)
    
    with open('sign_csr.conf', 'w') as f:
        f.write(sign_conf)
    
    # Generate CSRs
    subprocess.run(['openssl', 'req', '-new', '-key', 'server_auth.key',
                    '-out', 'auth.csr', '-config', 'auth_csr.conf'],
                   capture_output=True)
    subprocess.run(['openssl', 'req', '-new', '-key', 'server_sign.key',
                    '-out', 'sign.csr', '-config', 'sign_csr.conf'],
                   capture_output=True)
    
    # Read CSRs
    with open('auth.csr') as f:
        auth_csr = f.read()
    with open('sign.csr') as f:
        sign_csr = f.read()
    
    return auth_csr, sign_csr

def register_security_server():
    """Complete registration workflow"""
    
    # ===== STEP 1: Generate CSRs =====
    print("Step 1: Generating dual CSRs...")
    auth_csr, sign_csr = generate_dual_csrs("SECURITY_SERVER_1")
    print("✓ Generated auth.csr and sign.csr")
    
    # ===== STEP 2: Request Certificates from CA =====
    print("\nStep 2: Requesting certificates from CA...")
    step2_response = requests.post(
        'http://localhost:9000/api/security-servers/request-certificates',
        json={
            'server_id': 'SECURITY_SERVER_1',
            'server_name': 'Primary Security Gateway',
            'organization': 'My Organization',
            'auth_csr': auth_csr,
            'sign_csr': sign_csr,
            'address': '10.0.0.50',
            'network_instance': 'EE'
        }
    )
    
    if step2_response.status_code != 200:
        print(f"✗ Failed: {step2_response.text}")
        return
    
    step2_data = step2_response.json()
    print("✓ Received certificates from CA")
    print(f"  AUTH Certificate ID: {step2_data['auth_certificate']['certificate_id']}")
    print(f"  SIGN Certificate ID: {step2_data['sign_certificate']['certificate_id']}")
    
    # ===== STEP 3: Register with Global Server =====
    print("\nStep 3: Registering security server...")
    step3_response = requests.post(
        'http://localhost:9000/api/security-servers/register',
        json={
            'registration_id': 'REG_SS_001',
            'server_id': 'SECURITY_SERVER_1',
            'server_name': 'Primary Security Gateway',
            'organization': 'My Organization',
            'address': '10.0.0.50',
            'port': 9001,
            'network_instance': 'EE',
            'auth_csr': auth_csr,
            'auth_crt': step2_data['auth_certificate']['crt_file'],
            'auth_certificate_id': step2_data['auth_certificate']['certificate_id'],
            'auth_thumbprint': step2_data['auth_certificate']['thumbprint'],
            'auth_expiry_date': step2_data['auth_certificate']['expiry_date'],
            'sign_csr': sign_csr,
            'sign_crt': step2_data['sign_certificate']['crt_file'],
            'sign_certificate_id': step2_data['sign_certificate']['certificate_id'],
            'sign_thumbprint': step2_data['sign_certificate']['thumbprint'],
            'sign_expiry_date': step2_data['sign_certificate']['expiry_date'],
            'created_by': 'admin@organization.com'
        }
    )
    
    if step3_response.status_code != 200:
        print(f"✗ Failed: {step3_response.text}")
        return
    
    step3_data = step3_response.json()
    print("✓ Server registered successfully")
    print(f"  Registration ID: {step3_data['registration']['registration_id']}")
    
    # ===== STEP 4: Save Files Locally =====
    print("\nStep 4: Saving certificates locally...")
    
    Path('SECURITY_SERVER_1_auth.crt').write_text(
        step3_data['crt_files']['auth']['content']
    )
    print("✓ Saved: SECURITY_SERVER_1_auth.crt")
    
    Path('SECURITY_SERVER_1_sign.crt').write_text(
        step3_data['crt_files']['sign']['content']
    )
    print("✓ Saved: SECURITY_SERVER_1_sign.crt")
    
    Path('SECURITY_SERVER_1_registration.metadata').write_text(
        step3_data['metadata']['content']
    )
    print("✓ Saved: SECURITY_SERVER_1_registration.metadata")
    
    print("\n" + "="*60)
    print("REGISTRATION COMPLETE!")
    print("="*60)
    print(f"Server: {step3_data['registration']['server_id']}")
    print(f"Status: {step3_data['registration']['status']}")
    print(f"Registered at: {step3_data['registration']['registered_at']}")
    
    return step3_data

if __name__ == "__main__":
    register_security_server()
```

---

## Database Schema

### security_server_registrations Table

```sql
CREATE TABLE security_server_registrations (
    registration_id VARCHAR(100) PRIMARY KEY,
    server_id VARCHAR(100) UNIQUE NOT NULL,
    server_name VARCHAR(255) NOT NULL,
    organization VARCHAR(255) NOT NULL,
    address VARCHAR(100) NOT NULL,
    port INT NOT NULL,
    network_instance VARCHAR(50) DEFAULT 'EE',
    
    -- AUTH Certificate Fields
    auth_csr LONGTEXT NOT NULL,
    auth_crt LONGTEXT NOT NULL,
    auth_certificate_id VARCHAR(100) NOT NULL,
    auth_thumbprint VARCHAR(512) NOT NULL,
    auth_expiry_date TIMESTAMP,
    
    -- SIGN Certificate Fields
    sign_csr LONGTEXT NOT NULL,
    sign_crt LONGTEXT NOT NULL,
    sign_certificate_id VARCHAR(100) NOT NULL,
    sign_thumbprint VARCHAR(512) NOT NULL,
    sign_expiry_date TIMESTAMP,
    
    -- Metadata
    status VARCHAR(50) DEFAULT 'registered',
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    UNIQUE KEY unique_server (server_id),
    INDEX idx_auth_cert (auth_certificate_id),
    INDEX idx_sign_cert (sign_certificate_id)
);
```

---

## Management Endpoints

### List All Registrations

```bash
curl http://localhost:9000/api/security-servers/registrations | jq .
```

### Get Single Server Details

```bash
curl http://localhost:9000/api/security-servers/SECURITY_SERVER_1 | jq .
```

### Update Registration

```bash
curl -X PUT http://localhost:9000/api/security-servers/SECURITY_SERVER_1 \
  -H "Content-Type: application/json" \
  -d {'port': 9002, 'status': 'active'} | jq .
```

### Delete Registration

```bash
curl -X DELETE http://localhost:9000/api/security-servers/SECURITY_SERVER_1
```

---

## Error Responses

| Error | Status | Cause |
|-------|--------|-------|
| Server already registered | 409 | `server_id` already exists |
| CA certificate generation failed | 502 | CA service unreachable or failed |
| Database not configured | 400 | `/api/init-db` not called |
| Missing required fields | 400 | Incomplete request body |
| Database error | 500 | MySQL connection or query issue |

---

## Files Returned

### Certificate Files
- `{SERVER_ID}_auth.crt` - AUTH certificate for TLS/HTTPS
- `{SERVER_ID}_sign.crt` - SIGN certificate for message signing

### Metadata File
- `{SERVER_ID}_registration.metadata` - Registration details and certificate info

