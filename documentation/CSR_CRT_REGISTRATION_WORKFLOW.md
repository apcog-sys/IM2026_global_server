# Security Server Registration Workflow (CSR/CRT)

## Overview

The registration process uses standard PKI Certificate Signing Request (CSR) and Certificate (CRT) workflow:

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│  Security Svr   │         │  Global Server   │         │ CA Service   │
│   (Port: XXXX)  │         │  (Port: 9000)    │         │ (Port: 9002) │
└────────┬────────┘         └────────┬─────────┘         └──────┬───────┘
         │                           │                          │
         │ 1. Submit .csr file       │                          │
         │──────────────────────────>│                          │
         │                           │ 2. Forward CSR           │
         │                           │─────────────────────────>│
         │                           │                          │
         │                           │ 3. Verify & Sign CSR     │
         │                           │<─────────────────────────│
         │                           │ (Returns .crt file)      │
         │ 4. Get registration data  │                          │
         │ + verified .crt file      │                          │
         │<──────────────────────────│                          │
         │                           │                          │
         │ 5. Save .crt locally      │                          │
         │ .metadata file            │                          │
         │                           │                          │
```

## Workflow Steps

### Step 1: Generate Certificate Signing Request (CSR)

**Where**: Security Server (client-side)

Security server generates a CSR file locally:

```bash
# Generate private key
openssl genrsa -out server.key 2048

# Create a config file for CSR
cat > csr.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization
CN = SECURITY_SERVER_1

[v3_req]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
EOF

# Generate CSR
openssl req -new -key server.key -out server.csr -config csr.conf

# Convert CSR to PEM format for API submission
cat server.csr  # Copy content for API call
```

### Step 2: Submit CSR to Global Server for CA Verification

**Endpoint**: `POST /api/csr/verify`  
**Host**: Global Server (localhost:9000)

**Request Body**:
```json
{
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "csr_file": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA...\n-----END CERTIFICATE REQUEST-----",
  "address": "10.0.0.50",
  "network_instance": "EE"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "message": "CSR verified by CA and .crt file generated",
  "certificate_id": "cert-uuid-12345",
  "crt_file": "-----BEGIN CERTIFICATE-----\nMIIC9jCCAeYCCQCPHfIAKzR...\n-----END CERTIFICATE-----",
  "expiry_date": "2027-04-04T10:30:00Z",
  "thumbprint": "SHA256:ABCDEF1234567890...",
  "next_step": "Submit verified .crt file to /api/security-servers/register"
}
```

**Response (CA Verification Failed)**:
```json
{
  "status": "error",
  "message": "CSR verification failed: Invalid CSR format or signature mismatch"
}
```
**Status Code**: 400 Bad Request

### Step 3: Register Security Server with Verified Certificate

**Endpoint**: `POST /api/security-servers/register`  
**Host**: Global Server (localhost:9000)

**Request Body** (use values from Step 2 response):
```json
{
  "registration_id": "REG_SS_001",
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "address": "10.0.0.50",
  "port": 9001,
  "network_instance": "EE",
  "csr_file": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA...\n-----END CERTIFICATE REQUEST-----",
  "crt_file": "-----BEGIN CERTIFICATE-----\nMIIC9jCCAeYCCQCPHfIAKzR...\n-----END CERTIFICATE-----",
  "certificate_id": "cert-uuid-12345",
  "thumbprint": "SHA256:ABCDEF1234567890...",
  "created_by": "admin@example.com"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Security server registered successfully",
  "registration": {
    "registration_id": "REG_SS_001",
    "server_id": "SECURITY_SERVER_1",
    "status": "registered",
    "registered_at": "2026-04-04T10:35:00Z"
  },
  "certificate": {
    "certificate_id": "cert-uuid-12345",
    "thumbprint": "SHA256:ABCDEF1234567890..."
  },
  "crt_file": {
    "filename": "SECURITY_SERVER_1_registration.crt",
    "content": "-----BEGIN CERTIFICATE-----\nMIIC9jCCAeYCCQCPHfIAKzR...\n-----END CERTIFICATE-----",
    "instructions": "Save this .crt file in your security server's certificate directory"
  },
  "metadata": {
    "filename": "SECURITY_SERVER_1_registration.metadata",
    "content": "REGISTRATION-ID: REG_SS_001\nSERVER-ID: SECURITY_SERVER_1\n..."
  }
}
```

**Response (Server Already Registered)**:
```json
{
  "status": "error",
  "message": "Security server with ID 'SECURITY_SERVER_1' is already registered"
}
```
**Status Code**: 409 Conflict

### Step 4: Save Files Locally

**Security Server** saves the returned files:

```bash
# Save the signed certificate
cat > SECURITY_SERVER_1_registration.crt << 'EOF'
[content from crt_file.content]
EOF

# Save metadata
cat > SECURITY_SERVER_1_registration.metadata << 'EOF'
[content from metadata.content]
EOF
```

## Complete Request Examples

### Using cURL

```bash
#!/bin/bash

# Step 1: Generate CSR locally
openssl genrsa -out server.key 2048
cat > csr.conf << EOF
[req]
distinguished_name = req_distinguished_name
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = My Organization
CN = SECURITY_SERVER_1
EOF

openssl req -new -key server.key -out server.csr -config csr.conf
CSR_CONTENT=$(cat server.csr | tr '\n' '\\n')

# Step 2: Submit CSR for verification
echo "=== Verifying CSR with CA ==="
CSR_RESPONSE=$(curl -s -X POST http://localhost:9000/api/csr/verify \
  -H "Content-Type: application/json" \
  -d "{
    \"server_id\": \"SECURITY_SERVER_1\",
    \"server_name\": \"Primary Gateway\",
    \"organization\": \"My Organization\",
    \"csr_file\": \"$CSR_CONTENT\",
    \"address\": \"10.0.0.50\",
    \"network_instance\": \"EE\"
  }")

echo $CSR_RESPONSE | jq .

# Extract values
CERT_ID=$(echo $CSR_RESPONSE | jq -r '.certificate_id')
CRT_FILE=$(echo $CSR_RESPONSE | jq -r '.crt_file')
THUMBPRINT=$(echo $CSR_RESPONSE | jq -r '.thumbprint')

# Step 3: Register server
echo ""
echo "=== Registering Security Server ==="
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:9000/api/security-servers/register \
  -H "Content-Type: application/json" \
  -d "{
    \"registration_id\": \"REG_SS_001\",
    \"server_id\": \"SECURITY_SERVER_1\",
    \"server_name\": \"Primary Gateway\",
    \"organization\": \"My Organization\",
    \"address\": \"10.0.0.50\",
    \"port\": 9001,
    \"network_instance\": \"EE\",
    \"csr_file\": \"$CSR_CONTENT\",
    \"crt_file\": \"$CRT_FILE\",
    \"certificate_id\": \"$CERT_ID\",
    \"thumbprint\": \"$THUMBPRINT\",
    \"created_by\": \"admin@example.com\"
  }")

echo $REGISTER_RESPONSE | jq .

# Step 4: Save files locally
echo ""
echo "=== Saving files locally ==="
SAVED_CRT=$(echo $REGISTER_RESPONSE | jq -r '.crt_file.content')
echo "$SAVED_CRT" > SECURITY_SERVER_1_registration.crt
echo "✓ Saved: SECURITY_SERVER_1_registration.crt"

SAVED_METADATA=$(echo $REGISTER_RESPONSE | jq -r '.metadata.content')
echo "$SAVED_METADATA" > SECURITY_SERVER_1_registration.metadata
echo "✓ Saved: SECURITY_SERVER_1_registration.metadata"
```

### Using Python

```python
import requests
import json
import subprocess

# Step 1: Generate CSR
subprocess.run([
    'openssl', 'genrsa', '-out', 'server.key', '2048'
], capture_output=True)

csr_config = """[req]
distinguished_name = req_distinguished_name
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = My Organization
CN = SECURITY_SERVER_1"""

with open('csr.conf', 'w') as f:
    f.write(csr_config)

subprocess.run([
    'openssl', 'req', '-new', '-key', 'server.key', 
    '-out', 'server.csr', '-config', 'csr.conf'
], capture_output=True)

with open('server.csr', 'r') as f:
    csr_content = f.read()

# Step 2: Submit CSR for verification
print("=== Verifying CSR with CA ===")
csr_response = requests.post(
    'http://localhost:9000/api/csr/verify',
    json={
        'server_id': 'SECURITY_SERVER_1',
        'server_name': 'Primary Gateway',
        'organization': 'My Organization',
        'csr_file': csr_content,
        'address': '10.0.0.50',
        'network_instance': 'EE'
    }
)

csr_data = csr_response.json()
print(json.dumps(csr_data, indent=2))

# Extract values
cert_id = csr_data['certificate_id']
crt_file = csr_data['crt_file']
thumbprint = csr_data['thumbprint']

# Step 3: Register server
print("\n=== Registering Security Server ===")
register_response = requests.post(
    'http://localhost:9000/api/security-servers/register',
    json={
        'registration_id': 'REG_SS_001',
        'server_id': 'SECURITY_SERVER_1',
        'server_name': 'Primary Gateway',
        'organization': 'My Organization',
        'address': '10.0.0.50',
        'port': 9001,
        'network_instance': 'EE',
        'csr_file': csr_content,
        'crt_file': crt_file,
        'certificate_id': cert_id,
        'thumbprint': thumbprint,
        'created_by': 'admin@example.com'
    }
)

register_data = register_response.json()
print(json.dumps(register_data, indent=2))

# Step 4: Save files locally
print("\n=== Saving files locally ===")
with open('SECURITY_SERVER_1_registration.crt', 'w') as f:
    f.write(register_data['crt_file']['content'])
print("✓ Saved: SECURITY_SERVER_1_registration.crt")

with open('SECURITY_SERVER_1_registration.metadata', 'w') as f:
    f.write(register_data['metadata']['content'])
print("✓ Saved: SECURITY_SERVER_1_registration.metadata")
```

## Management Endpoints

### List All Registrations

```bash
curl http://localhost:9000/api/security-servers/registrations
```

**Response**:
```json
[
  {
    "registration_id": "REG_SS_001",
    "server_id": "SECURITY_SERVER_1",
    "server_name": "Primary Gateway",
    "organization": "My Organization",
    "status": "registered",
    "created_at": "2026-04-04T10:35:00Z"
  }
]
```

### Get Single Server Details

```bash
curl http://localhost:9000/api/security-servers/SECURITY_SERVER_1
```

**Response**:
```json
{
  "registration_id": "REG_SS_001",
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "address": "10.0.0.50",
  "port": 9001,
  "network_instance": "EE",
  "certificate_id": "cert-uuid-12345",
  "thumbprint": "SHA256:ABCDEF1234567890...",
  "status": "registered",
  "expiry_date": "2027-04-04T10:30:00Z",
  "created_at": "2026-04-04T10:35:00Z"
}
```

### Update Server Registration

```bash
curl -X PUT http://localhost:9000/api/security-servers/SECURITY_SERVER_1 \
  -H "Content-Type: application/json" \
  -d '{
    "port": 9002,
    "status": "active"
  }'
```

### Delete Registration

```bash
curl -X DELETE http://localhost:9000/api/security-servers/SECURITY_SERVER_1
```

**Response**:
```json
{
  "status": "success",
  "message": "Security server deregistered"
}
```

## Database Schema

### security_server_registrations Table

| Column | Type | Description |
|--------|------|-------------|
| `registration_id` | VARCHAR(100) | Primary key, unique registration ID |
| `server_id` | VARCHAR(100) | UNIQUE, security server identifier |
| `server_name` | VARCHAR(255) | Display name of security server |
| `organization` | VARCHAR(255) | Organization name |
| `address` | VARCHAR(100) | Server IP/hostname |
| `port` | INT | Server port number |
| `network_instance` | VARCHAR(50) | Network instance code (e.g., "EE") |
| `certificate_id` | VARCHAR(100) | Certificate ID from CA |
| `thumbprint` | VARCHAR(512) | Certificate thumbprint (SHA256) |
| `csr_file` | LONGTEXT | Original CSR content (PEM) |
| `crt_file` | LONGTEXT | Signed certificate from CA (PEM) |
| `expiry_date` | TIMESTAMP | Certificate expiration date |
| `status` | VARCHAR(50) | Status: registered, active, inactive |
| `created_by` | VARCHAR(255) | User who registered the server |
| `created_at` | TIMESTAMP | Registration timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

## Error Codes

| Status | Code | Message | Cause |
|--------|------|---------|-------|
| 400 | Bad Request | CSR verification failed | Invalid CSR format or CA rejected it |
| 400 | Bad Request | Database not configured | DB config endpoint not called first |
| 409 | Conflict | Server already registered | Duplicate server_id |
| 502 | Bad Gateway | CA service error | CA service (port 9002) unreachable or failed |
| 500 | Server Error | Database error | MySQL connection or query issue |

## Security Considerations

1. **CSR Validation**: Global Server forwards CSR to CA without modification
2. **Certificate Verification**: CA verifies CSR signature and organization details
3. **File Storage**: CSR and CRT stored in LONGTEXT for audit trail
4. **Thumbprint Tracking**: Certificate thumbprint stored for identity verification
5. **Expiry Monitoring**: Certificate expiry date tracked for renewal alerts

## Usage Scenario

1. **Security Server Administrator** generates CSR with valid organization information
2. **Security Server** sends CSR to Global Server (`/api/csr/verify` endpoint)
3. **Global Server** forwards CSR to CA Service on port 9002
4. **CA Service** verifies CSR and signs it, returns .crt file
5. **Security Server** receives verified .crt and registration metadata
6. **Security Server** stores .crt locally for HTTPS/TLS configuration
7. **Security Server** can now communicate securely with the federated network

## Testing

```bash
# Initialize database
curl -X POST http://localhost:9000/api/init-db \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "password",
    "database": "system_config"
  }'

# Generate CSR and verify
# (run the bash script above)
```

