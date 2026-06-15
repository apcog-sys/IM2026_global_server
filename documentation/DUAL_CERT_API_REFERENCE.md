# Dual CSR/CRT Registration - API Quick Reference

## 2 Main Endpoints

### Endpoint 1: Request Certificates
**POST** `/api/security-servers/request-certificates`

Submits dual CSRs (AUTH + SIGN) to CA for verification and signing.

**Request**:
```json
{
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "auth_csr": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA...\n-----END CERTIFICATE REQUEST-----",
  "sign_csr": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA...\n-----END CERTIFICATE REQUEST-----",
  "address": "10.0.0.50",
  "network_instance": "EE"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "auth_certificate": {
    "certificate_id": "uuid-1",
    "certificate_type": "auth",
    "crt_file": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "thumbprint": "SHA256:...",
    "expiry_date": "2027-04-09T10:30:00Z"
  },
  "sign_certificate": {
    "certificate_id": "uuid-2",
    "certificate_type": "sign",
    "crt_file": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "thumbprint": "SHA256:...",
    "expiry_date": "2027-04-09T10:30:00Z"
  }
}
```

---

### Endpoint 2: Register Security Server
**POST** `/api/security-servers/register`

Registers server with dual verified certificates. Stores .csr and .crt for both AUTH and SIGN in database.

**Request**:
```json
{
  "registration_id": "REG_SS_001",
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "address": "10.0.0.50",
  "port": 9001,
  "network_instance": "EE",
  
  "auth_csr": "[from step 1]",
  "auth_crt": "[from endpoint 1 response]",
  "auth_certificate_id": "[from endpoint 1 response]",
  "auth_thumbprint": "[from endpoint 1 response]",
  "auth_expiry_date": "[from endpoint 1 response]",
  
  "sign_csr": "[from step 1]",
  "sign_crt": "[from endpoint 1 response]",
  "sign_certificate_id": "[from endpoint 1 response]",
  "sign_thumbprint": "[from endpoint 1 response]",
  "sign_expiry_date": "[from endpoint 1 response]",
  
  "created_by": "admin@organization.com"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "registration": {
    "registration_id": "REG_SS_001",
    "server_id": "SECURITY_SERVER_1",
    "status": "registered",
    "registered_at": "2026-04-09T10:35:00Z"
  },
  "certificates": {
    "auth": {
      "certificate_id": "uuid-1",
      "thumbprint": "SHA256:...",
      "expiry_date": "2027-04-09T10:30:00Z"
    },
    "sign": {
      "certificate_id": "uuid-2",
      "thumbprint": "SHA256:...",
      "expiry_date": "2027-04-09T10:30:00Z"
    }
  },
  "crt_files": {
    "auth": {
      "filename": "SECURITY_SERVER_1_auth.crt",
      "content": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
    },
    "sign": {
      "filename": "SECURITY_SERVER_1_sign.crt",
      "content": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
    }
  },
  "metadata": {
    "filename": "SECURITY_SERVER_1_registration.metadata",
    "content": "[registration details]"
  }
}
```

---

## Example cURL Commands

### Full workflow
```bash
#!/bin/bash

# Generate CSRs
openssl genrsa -out server_auth.key 2048
openssl req -new -key server_auth.key -out auth.csr -subj "/C=US/O=Org/CN=SS1.auth"

openssl genrsa -out server_sign.key 2048
openssl req -new -key server_sign.key -out sign.csr -subj "/C=US/O=Org/CN=SS1.sign"

AUTH_CSR=$(cat auth.csr | tr '\n' '\\n')
SIGN_CSR=$(cat sign.csr | tr '\n' '\\n')

# Step 1: Request certificates
R1=$(curl -s -X POST http://localhost:9000/api/security-servers/request-certificates \
  -H "Content-Type: application/json" \
  -d "{\"server_id\":\"SECURITY_SERVER_1\",\"server_name\":\"Primary\",\"organization\":\"Org\",\"auth_csr\":\"$AUTH_CSR\",\"sign_csr\":\"$SIGN_CSR\",\"address\":\"10.0.0.50\",\"network_instance\":\"EE\"}")

AUTH_CRT=$(echo $R1 | jq -r '.auth_certificate.crt_file')
AUTH_ID=$(echo $R1 | jq -r '.auth_certificate.certificate_id')
AUTH_THUMB=$(echo $R1 | jq -r '.auth_certificate.thumbprint')
AUTH_EXP=$(echo $R1 | jq -r '.auth_certificate.expiry_date')

SIGN_CRT=$(echo $R1 | jq -r '.sign_certificate.crt_file')
SIGN_ID=$(echo $R1 | jq -r '.sign_certificate.certificate_id')
SIGN_THUMB=$(echo $R1 | jq -r '.sign_certificate.thumbprint')
SIGN_EXP=$(echo $R1 | jq -r '.sign_certificate.expiry_date')

echo "✓ Got certificates from CA"

# Step 2: Register
R2=$(curl -s -X POST http://localhost:9000/api/security-servers/register \
  -H "Content-Type: application/json" \
  -d "{\"registration_id\":\"REG_SS_001\",\"server_id\":\"SECURITY_SERVER_1\",\"server_name\":\"Primary\",\"organization\":\"Org\",\"address\":\"10.0.0.50\",\"port\":9001,\"network_instance\":\"EE\",\"auth_csr\":\"$AUTH_CSR\",\"auth_crt\":\"$AUTH_CRT\",\"auth_certificate_id\":\"$AUTH_ID\",\"auth_thumbprint\":\"$AUTH_THUMB\",\"auth_expiry_date\":\"$AUTH_EXP\",\"sign_csr\":\"$SIGN_CSR\",\"sign_crt\":\"$SIGN_CRT\",\"sign_certificate_id\":\"$SIGN_ID\",\"sign_thumbprint\":\"$SIGN_THUMB\",\"sign_expiry_date\":\"$SIGN_EXP\",\"created_by\":\"admin@org.com\"}")

echo $R2 | jq .

# Save files
echo $R2 | jq -r '.crt_files.auth.content' > SECURITY_SERVER_1_auth.crt
echo $R2 | jq -r '.crt_files.sign.content' > SECURITY_SERVER_1_sign.crt
echo $R2 | jq -r '.metadata.content' > SECURITY_SERVER_1_registration.metadata

echo "✓ Saved .crt files"
```

---

## Data Flow

```
Step 1: Generate CSRs (LOCAL)
  ├─ auth.csr ─────────┐
  └─ sign.csr ──────────┼─→ Submit to Endpoint 1
                        │
Step 2: Request Certificates (ENDPOINT 1)
  ├─ Forward auth.csr to CA
  │  └─→ CA verifies & signs → auth.crt + auth_thumbprint
  ├─ Forward sign.csr to CA
  │  └─→ CA verifies & signs → sign.crt + sign_thumbprint
  └─→ Response: auth.crt, sign.crt + metadata
                        │
Step 3: Register (ENDPOINT 2)
  ├─ Store in DB:
  │  ├─ auth_csr + auth_crt + auth_certificate_id + auth_thumbprint
  │  ├─ sign_csr + sign_crt + sign_certificate_id + sign_thumbprint
  │  └─ Other metadata
  └─→ Response: Both .crt files for local storage
                        │
Step 4: Save Locally (CLIENT)
  ├─ SS_1_auth.crt ────── For TLS/HTTPS
  ├─ SS_1_sign.crt ────── For message signing
  └─ SS_1_registration.metadata
```

---

## What Gets Stored in Database

| Field | Content | Purpose |
|-------|---------|---------|
| `auth_csr` | PEM text | Original AUTH CSR for audit trail |
| `auth_crt` | PEM text | Signed AUTH certificate from CA |
| `auth_certificate_id` | UUID | CA-assigned certificate ID |
| `auth_thumbprint` | SHA256 hash | Certificate fingerprint for verification |
| `sign_csr` | PEM text | Original SIGN CSR for audit trail |
| `sign_crt` | PEM text | Signed SIGN certificate from CA |
| `sign_certificate_id` | UUID | CA-assigned certificate ID |
| `sign_thumbprint` | SHA256 hash | Certificate fingerprint for verification |

---

## Management Endpoints

```bash
# List all registrations
GET /api/security-servers/registrations

# Get single server
GET /api/security-servers/SECURITY_SERVER_1

# Update server
PUT /api/security-servers/SECURITY_SERVER_1
Body: {"port": 9002, "status": "active"}

# Delete server
DELETE /api/security-servers/SECURITY_SERVER_1
```

---

## What Authentication Comes From CA

### From `/api/certificates/generate-auth` (Port 9002)
```
Input:  auth.csr (or public key)
Output: {
  "certificate_id": "uuid",
  "certificate_type": "auth",
  "certificate_pem": "[CERTIFICATE]",
  "thumbprint": "SHA256:...",
  "expiry_date": "2027-04-09T10:30:00Z"
}
```

### From `/api/certificates/generate-sign` (Port 9002)
```
Input:  sign.csr (or public key)
Output: {
  "certificate_id": "uuid",
  "certificate_type": "sign",
  "certificate_pem": "[CERTIFICATE]",
  "thumbprint": "SHA256:...",
  "expiry_date": "2027-04-09T10:30:00Z"
}
```

---

## Files Returned to Security Server

After Step 3 (Register), Security Server receives:

1. **`SECURITY_SERVER_1_auth.crt`**
   - Use for: HTTPS/TLS connections
   - Combine with `server_auth.key` for server certificate

2. **`SECURITY_SERVER_1_sign.crt`**
   - Use for: Message signing and verification
   - Combine with `server_sign.key` for signing operations

3. **`SECURITY_SERVER_1_registration.metadata`**
   - Contains: Registration ID, server details, certificate info
   - Use for: Records and audits

