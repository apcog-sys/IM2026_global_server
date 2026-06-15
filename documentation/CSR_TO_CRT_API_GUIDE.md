# 🔐 CSR to CRT Conversion - Complete API Guide

## 📋 Overview

You now have **two ways** to generate certificates:

1. **Direct CSR Signing** - Send CSR → Get .crt file (NEW)
2. **Public Key Signing** - Send public key → Get .crt file (Existing)

---

## 🆕 Method 1: Direct CSR → CRT Signing (Recommended)

**This is what you asked for!** Send a CSR and get back a signed certificate.

### API Endpoint

```
POST /api/certificates/sign-csr
```

**URL:** `http://localhost:9002/api/certificates/sign-csr`

### Request

```json
{
  "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\nMIICpjCCAY4CAQAwEzERMA8GA1UEAwwIVEVTVF9HVzAwMTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBAOGd1UuSSXHbN8X5+xMShmyJS21yjjCQCu8KmhqYEnT\nQ/hLuP6krPzXpTx+TpjXxCQLpIuJ6rO7CZ9Q5vV8QmWn7xU3ZqZ3Z3Z3Z3Z3Z3Z3Z\n-----END CERTIFICATE REQUEST-----",
  "server_id": "TEST_GW001",
  "cert_type": "auth"
}
```

**Parameters:**
- `csr_pem` (string, **required**) - CSR in PEM format (with newlines or escaped `\n`)
- `server_id` (string, **required**) - Server ID (e.g., "TEST_GW001")
- `cert_type` (string, optional) - `"auth"` (default) or `"sign"`

### Response

```json
{
  "status": "success",
  "certificate_pem": "-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIBATANBgkqhkiG9w0BAQsFADCBhDELMAkGA1UEBhMCRUUx\n-----END CERTIFICATE-----",
  "certificate_id": "550e8400-e29b-41d4-a716-446655440000",
  "server_id": "TEST_GW001",
  "certificate_type": "auth",
  "issued_date": "2026-04-15T10:30:00+00:00",
  "expiry_date": "2027-04-15T10:30:00+00:00",
  "thumbprint": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "message": "CSR signed successfully (auth certificate)"
}
```

### cURL Example

```bash
curl -X POST http://localhost:9002/api/certificates/sign-csr \
  -H "Content-Type: application/json" \
  -d '{
    "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\nMIICpjCCAY4CAQAwEzERMA8GA1UEAwwIVEVTVF9HVzAwMTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBAOGd1UuSSXHbN8X5+xMShmyJS21yjjCQCu8KmhqYEnT\n-----END CERTIFICATE REQUEST-----",
    "server_id": "TEST_GW001",
    "cert_type": "auth"
  }'
```

### Python Example

```python
import requests
import json

# Read CSR from file
with open("csr.pem", "r") as f:
    csr_data = f.read()

# Prepare request
payload = {
    "csr_pem": csr_data,
    "server_id": "TEST_GW001",
    "cert_type": "auth"
}

# Send to CA Service
response = requests.post(
    "http://localhost:9002/api/certificates/sign-csr",
    json=payload
)

if response.status_code == 201:
    result = response.json()
    
    # Extract certificate
    cert_pem = result["certificate_pem"]
    
    # Save certificate to .crt file
    with open("certificate.crt", "w") as f:
        f.write(cert_pem)
    
    print(f"✅ Certificate saved: {result['certificate_id']}")
    print(f"  Valid From: {result['issued_date']}")
    print(f"  Valid To: {result['expiry_date']}")
else:
    print(f"❌ Error: {response.text}")
```

---

## 📊 Method 2: Public Key → CRT (Existing)

If you have a public key instead of CSR:

```
POST /api/certificates/generate-auth
POST /api/certificates/generate-sign
```

**Request:**
```json
{
  "server_id": "TEST_GW001",
  "server_name": "test-gateway",
  "organization": "My Org",
  "address": "192.168.1.100",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
}
```

---

## 🔄 Complete Workflow (Frontend + Backend)

### Step 1: Generate CSR (on server)
```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Generate CSR
openssl req -new -key private_key.pem -out csr.pem \
  -subj "/C=EE/ST=Harjumaa/L=Tallinn/O=MyOrg/CN=TEST_GW001"
```

### Step 2: Send CSR to CA Service
```bash
curl -X POST http://localhost:9002/api/certificates/sign-csr \
  -H "Content-Type: application/json" \
  -d "{
    \"csr_pem\": \"$(cat csr.pem | tr '\n' '\\n')\",
    \"server_id\": \"TEST_GW001\",
    \"cert_type\": \"auth\"
  }" | jq '.certificate_pem' -r > certificate.crt
```

### Step 3: Verify Certificate
```bash
openssl x509 -in certificate.crt -text -noout

# Check expiry
openssl x509 -in certificate.crt -noout -dates
```

---

## 🎯 Integration with Global Server (Port 9000)

If you want to sign CSRs through the Global Server (gs1.py) instead of directly to CA:

```bash
# Frontend sends CSR to Global Server
POST /api/sign-csr
{
  "csr_id": 2,
  "csr_pem": "...",
  "server_id": "TEST_GW001",
  "cert_type": "auth"
}
```

**Backend Flow:**
1. Accept CSR from frontend
2. Forward to CA Service (port 9002)
3. Store signed certificate in `certificates` table
4. Update `certificate_requests` status to SIGNED
5. Return certificate to frontend

---

## 📁 File Operations

### Save CSR to .pem file
```bash
# Extract CSR from database and save
mysql -uroot -proot gs1 -e \
  "SELECT csr_data FROM certificate_requests WHERE csr_id=2" \
  | tail -1 > csr.pem
```

### Save Certificate to .crt file
```bash
# Extract certificate from response
echo "$CERT_PEM_FROM_API" > certificate.crt
```

### Verify both files
```bash
# View CSR
openssl req -in csr.pem -text -noout

# View CRT
openssl x509 -in certificate.crt -text -noout
```

---

## ✅ Validation Checklist

Before signing CSR, verify:

- [ ] CSR is valid PEM format
- [ ] CA Service is running on port 9002
- [ ] CA has initialized root certificate
- [ ] CSR public key matches later certificate signing

## 🔍 Troubleshooting

### Error: "Invalid CSR format"
```
❌ CSR_PEM must be valid PEM encoded certificate request
✅ Use: openssl req -in csr.pem -text to verify format
```

### Error: "Service not initialized"
```
❌ CA Manager not initialized
✅ Start CA Service: python CA_management/ca_service.py
```

### Error: "CSR parsing failed"
```
❌ CSR contains invalid data
✅ Regenerate CSR: openssl req -new -key private.key -out csr.pem
```

---

## 📊 Request/Response Examples

### Example 1: Sign AUTH Certificate

**Request:**
```json
{
  "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\nMIICpjCCAY4CAQAwEzERMA8GA1UEAwwITXlTZXJ2ZXIxCjAIBgNVBAgMAkVFMQsw\nCQYDVQQGEwJFRTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMPh5jcK\nzXx4vX...\n-----END CERTIFICATE REQUEST-----",
  "server_id": "GATEWAY_01",
  "cert_type": "auth"
}
```

**Response:**
```json
{
  "status": "success",
  "certificate_id": "8f47a3c8-1234-5678-9abc-def012345678",
  "server_id": "GATEWAY_01",
  "certificate_type": "auth",
  "certificate_pem": "-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIBATANBgkqhkiG9w0BAQsFADCBhDELMAkGA1UEBhMCRUUx\nETAPBgNVBAgMAkhhcmp1bWFhMREwDwYDVQQHDAhUYWxsaW5uMRswGQYDVQQKDBJU\nb3J1c3QgQXV0aG9yaXR5MRswGQYDVQQDDBJSb290IENlcnRpZmljYXRpb24wHhcN\nMjYwNDE1MTAzMDAwWhcNMjcwNDE1MTAzMDAwWjBRMQswCQYDVQQGEwJFRTERMA8G\nA1UECAwISGFyanVtYWExETAPBgNVBAcMCFRhbGxpbm4xDzANBgNVBAoMBk15T3Jn\nMRQwEgYDVQQDDAtBVVRILUdBVEVXQVkwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAw\nggEKAoIBAQDh4eY3Cs18eL1/hMShmyJS21yjjCQCu8KmhqYEnT+FK4/qSs/NelPH\n5OmNfEJAuki4nqs7sJn1Dm9XxCZafvFTdmpnZnZnZnZnZnZnZnZnZnZnZnZnZmZm\nZn...\n-----END CERTIFICATE-----",
  "issued_date": "2026-04-15T10:30:00+00:00",
  "expiry_date": "2027-04-15T10:30:00+00:00",
  "thumbprint": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "message": "CSR signed successfully (auth certificate)"
}
```

### Example 2: Sign SIGN Certificate

**Request:**
```json
{
  "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\n...",
  "server_id": "SIGNER_02",
  "cert_type": "sign"
}
```

---

## 🚀 Quick Start Script

```bash
#!/bin/bash

# 1. Generate CSR
openssl req -new -keyout private.key -out csr.pem \
  -subj "/C=EE/ST=Harjumaa/L=Tallinn/O=MyOrg/CN=MY_SERVER"

echo "✅ CSR generated"

# 2. Read CSR content
CSR_CONTENT=$(cat csr.pem | tr '\n' '\\n')

# 3. Send to CA Service
RESPONSE=$(curl -s -X POST http://localhost:9002/api/certificates/sign-csr \
  -H "Content-Type: application/json" \
  -d "{
    \"csr_pem\": \"$CSR_CONTENT\",
    \"server_id\": \"MY_SERVER\",
    \"cert_type\": \"auth\"
  }")

# 4. Extract certificate
echo "$RESPONSE" | jq '.certificate_pem' -r > certificate.crt

echo "✅ Certificate saved to: certificate.crt"
echo ""
echo "Certificate details:"
openssl x509 -in certificate.crt -noout -dates
```

---

## 📝 API Endpoints Summary

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/api/certificates/sign-csr` | POST | Sign CSR → CRT | CSR PEM | Signed Certificate |
| `/api/certificates/generate-auth` | POST | Generate from public key | Public Key | AUTH Certificate |
| `/api/certificates/generate-sign` | POST | Generate from public key | Public Key | SIGN Certificate |
| `/api/certificates/ca-root` | GET | Get CA root cert | - | CA Certificate |
| `/api/certificates/{cert_id}` | GET | Get certificate | Cert ID | Certificate Details |
| `/health` | GET | Service health | - | Status |

---

## ✨ Benefits

✅ **Direct CSR signing** - No need to extract/manage public keys separately
✅ **CSR preservation** - Keep original CSR data for audit
✅ **Standard format** - Uses industry-standard X.509 certificates
✅ **Proper extensions** - Adds TLS/Code Signing extensions based on type
✅ **Database ready** - Integrates with existing certificate storage

