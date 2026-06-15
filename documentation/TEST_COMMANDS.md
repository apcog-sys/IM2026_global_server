# 🧪 Ready-to-Use Test Commands - Copy & Paste

## Test Setup

> **Note**: Database configuration is automatically loaded from `config.json` on server startup.
> No manual initialization needed - just start and use!

### Start Server
```bash
python gs1.py
```

Server will automatically:
- Load database config from `config.json`
- Connect to existing MySQL database (gs1)
- Ready to accept API requests on port 9000

---

## CRUD Operations by Resource

### 1. ENTITIES CRUD

#### CREATE Entity
```bash
curl -X POST http://localhost:9000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "TEST_ORG",
    "entity_name": "Test Organization",
    "entity_type": "Organization",
    "status": "ACTIVE"
  }' | python -m json.tool
```

#### READ All Entities
```bash
curl http://localhost:9000/api/entities | python -m json.tool
```

#### READ Single Entity
```bash
curl http://localhost:9000/api/entities/1 | python -m json.tool
```

#### UPDATE Entity
```bash
curl -X PUT http://localhost:9000/api/entities/1 \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Updated Organization Name",
    "status": "ACTIVE"
  }' | python -m json.tool
```

#### DELETE Entity
```bash
curl -X DELETE http://localhost:9000/api/entities/1
```

---

### 2. NETWORK CONFIG CRUD

#### CREATE Network Config (Gateway Registration)
```bash
curl -X POST http://localhost:9000/api/network-config \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Security Gateway",
    "version": "2.0",
    "network_instance": "TEST",
    "gateway_code": "TEST_GW001",
    "entity_id": 1,
    "host": "192.168.1.100",
    "port": 9001,
    "hostname": "test-gateway.local",
    "ip_address": "192.168.1.100",
    "environment": "Testing"
  }' | python -m json.tool
```

#### READ All Network Configs
```bash
curl http://localhost:9000/api/network-config | python -m json.tool
```

#### READ Single Network Config
```bash
curl http://localhost:9000/api/network-config/TEST_GW001 | python -m json.tool
```

#### UPDATE Network Config
```bash
curl -X PUT http://localhost:9000/api/network-config/TEST_GW001 \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "updated-gateway.local",
    "environment": "Production"
  }' | python -m json.tool
```

#### DELETE Network Config
```bash
curl -X DELETE http://localhost:9000/api/network-config/TEST_GW001
```

---

### 3. SERVER KEYS CRUD

#### CREATE Server Key (AUTH)
```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_type": "AUTH",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ExKG\nLklLbXKOMJAK7wqaGrQSdP7MjLjOpKJPzXpTx+TpjXxCQLpIuJ6rO7CZ9Q5vV8Qm\nWn7xU3ZqZ3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z\n-----END PUBLIC KEY-----"
  }' | python -m json.tool
```

#### CREATE Server Key (SIGN)
```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_type": "SIGN",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx9VTQ5JCQs3wtXKcM9qC\n4x9RJ0L6M2Q1p8C3O9Q9s8vL4xP2U5V6q7s8T3U4Y5Z6a7b8C9d0E1f2G3h4I5j6\nK7l8M9n0O1p2Q3r4S5t6U7v8W9x0Y1z2A3b4C5d6E7f8G9h0I1j2K3l4M5n6O7p8\n-----END PUBLIC KEY-----"
  }' | python -m json.tool
```

#### READ All Server Keys
```bash
curl http://localhost:9000/api/server-keys | python -m json.tool
```

#### READ Single Server Key
```bash
curl http://localhost:9000/api/server-keys/1 | python -m json.tool
```

#### READ Server Keys by Gateway
```bash
curl http://localhost:9000/api/server-keys/gateway/TEST_GW001 | python -m json.tool
```

#### UPDATE Server Key
```bash
curl -X PUT http://localhost:9000/api/server-keys/1 \
  -H "Content-Type: application/json" \
  -d '{
    "key_type": "AUTH",
    "public_key": "-----BEGIN PUBLIC KEY-----\n[updated key]\n-----END PUBLIC KEY-----"
  }' | python -m json.tool
```

#### DELETE Server Key
```bash
curl -X DELETE http://localhost:9000/api/server-keys/1
```

---

### 4. CSR REGISTRATION CRUD (Certificate Requests)

#### Prepare CSR File for Upload

First, save your CSR file locally (e.g., `auth_csr.pem`), then read it for upload:

```bash
# Option 1: Direct from file with Python (Unix/Linux/Mac)
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d "{
    \"gateway_code\": \"TEST_GW001\",
    \"key_id\": 1,
    \"cert_type\": \"AUTH\",
    \"csr_data\": $(python3 -c "import json; print(json.dumps(open('auth_csr.pem').read()))")
  }" | python -m json.tool
```

```bash
# Option 2: Windows PowerShell
$csr = Get-Content -Path "auth_csr.pem" -Raw
$json = @{
    gateway_code = "TEST_GW001"
    key_id = 1
    cert_type = "AUTH"
    csr_data = $csr
} | ConvertTo-Json
$json | curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d @-
```

#### CREATE Certificate Request - AUTH CSR
```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCFUExFTATBgNVBAgMDFRlc3RUb3duLlVM\nMRQwEgYDVQQHDAtUZXN0Q291bnRyeTEPMA0GA1UECgwGVGVzdENvMQswCQYDVQQD\nDAJBVTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5\n/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLECAwEAAaA2MDAw\nBgMCABAME1Rlc3RBcC5QbGFjZWhvbGRlcjELBgNVBAwEA1VTQzANBgkqhkiG9w0B\nAQUFAAOCAQEA1Z3VS5JJcds3xfn/ExKGLklLBZqLpV2S7PLD1/Q2\n-----END CERTIFICATE REQUEST-----"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "AUTH CSR registered successfully",
  "csr_id": 1
}
```

---

#### CREATE Certificate Request - SIGN CSR
```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 2,
    "cert_type": "SIGN",
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCR0ExFTATBgNVBAgMDFRlc3RQcm9WYWxs\nMRQwEgYDVQQHDAtUZXN0U3RhY2tvdmVyMQ8wDQYDVQQKDAZUZXN0Q29YDVAYDVQD\nDAJTRzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5\n/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLExAwaEAwEAAaA2MDAw\nBgMCABAME1Rlc3RBcC5QbGFjZWhvbGRlcjELBgNVBAwEA1VTQzANBgkqhkiG9w0B\nAQUFAAOCAQEA1Z3VS5JJcds3xfn/ExKGLklLBZqLpV2S7PLD1/Q2\n-----END CERTIFICATE REQUEST-----"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "SIGN CSR registered successfully",
  "csr_id": 2
}
```

---

#### READ All Certificate Requests
```bash
curl http://localhost:9000/api/certificate-requests | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "total": 2,
  "requests": [
    {
      "csr_id": 1,
      "gateway_code": "TEST_GW001",
      "key_id": 1,
      "cert_type": "AUTH",
      "status": "PENDING",
      "requested_at": "2026-04-14T10:30:00"
    },
    {
      "csr_id": 2,
      "gateway_code": "TEST_GW001",
      "key_id": 2,
      "cert_type": "SIGN",
      "status": "PENDING",
      "requested_at": "2026-04-14T10:31:00"
    }
  ]
}
```

---

#### READ All AUTH CSRs (Filter by cert_type)
```bash
curl "http://localhost:9000/api/certificate-requests?cert_type=AUTH" | python -m json.tool
```

---

#### READ All PENDING CSRs (Filter by status)
```bash
curl "http://localhost:9000/api/certificate-requests?status=PENDING" | python -m json.tool
```

---

#### READ All SIGNED CSRs
```bash
curl "http://localhost:9000/api/certificate-requests?status=SIGNED" | python -m json.tool
```

---

#### READ Single Certificate Request
```bash
curl http://localhost:9000/api/certificate-requests/1 | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "request": {
    "csr_id": 1,
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
    "status": "PENDING",
    "requested_at": "2026-04-14T10:30:00"
  }
}
```

---

#### UPDATE CSR Status - Mark as SIGNED
```bash
curl -X PUT http://localhost:9000/api/certificate-requests/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "SIGNED"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "CSR status updated to SIGNED"
}
```

---

#### UPDATE CSR Status - Mark as REJECTED
```bash
curl -X PUT http://localhost:9000/api/certificate-requests/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "REJECTED"
  }' | python -m json.tool
```

---

#### DELETE Certificate Request
```bash
curl -X DELETE http://localhost:9000/api/certificate-requests/1 | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "CSR deleted successfully"
}
```

---

#### Bulk View All CSRs for a Gateway
```bash
# List both AUTH and SIGN CSRs for a specific gateway
curl "http://localhost:9000/api/certificate-requests?gateway_code=TEST_GW001" | python -m json.tool
```

---

#### CSR Registration Status Summary
```bash
# Check counts by status
echo "=== PENDING CSRs ===" && \
curl -s "http://localhost:9000/api/certificate-requests?status=PENDING" | head -20

echo -e "\n=== SIGNED CSRs ===" && \
curl -s "http://localhost:9000/api/certificate-requests?status=SIGNED" | head -20

echo -e "\n=== REJECTED CSRs ===" && \
curl -s "http://localhost:9000/api/certificate-requests?status=REJECTED" | head -20
```

---

### 5. CERTIFICATES CRUD

#### CREATE Certificate (AUTH)
```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\nBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\nMIIDBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\n-----END CERTIFICATE-----",
    "issued_by": "Test CA Authority",
    "valid_from": "2026-04-11T10:00:00",
    "valid_to": "2027-04-11T10:00:00"
  }' | python -m json.tool
```

#### READ All Certificates
```bash
curl http://localhost:9000/api/certificates | python -m json.tool
```

#### READ Single Certificate
```bash
curl http://localhost:9000/api/certificates/1 | python -m json.tool
```

#### READ Certificates by Gateway
```bash
curl http://localhost:9000/api/certificates/gateway/TEST_GW001 | python -m json.tool
```

#### UPDATE Certificate
```bash
curl -X PUT http://localhost:9000/api/certificates/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ACTIVE"
  }' | python -m json.tool
```

#### DELETE Certificate
```bash
curl -X DELETE http://localhost:9000/api/certificates/1
```

---

### 6. REGISTRATION LOG CRUD

#### CREATE Registration Log Entry
```bash
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "action": "SUBMITTED",
    "performed_by": "system@test.com",
    "remarks": "Initial registration submission"
  }' | python -m json.tool
```

#### READ All Registration Logs
```bash
curl http://localhost:9000/api/registration-log | python -m json.tool
```

#### READ Single Registration Log
```bash
curl http://localhost:9000/api/registration-log/1 | python -m json.tool
```

#### READ Logs by Gateway
```bash
curl http://localhost:9000/api/registration-log/gateway/TEST_GW001 | python -m json.tool
```

#### UPDATE Registration Log
```bash
curl -X PUT http://localhost:9000/api/registration-log/1 \
  -H "Content-Type: application/json" \
  -d '{
    "action": "APPROVED",
    "performed_by": "admin@test.com",
    "remarks": "Gateway approved for production"
  }' | python -m json.tool
```

#### DELETE Registration Log
```bash
curl -X DELETE http://localhost:9000/api/registration-log/1
```

---

### 7. GLOBAL DIRECTORY CRUD

#### CREATE Global Directory Entry
```bash
curl -X POST http://localhost:9000/api/global-directory \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "TEST_ORG",
    "gateway_code": "TEST_GW001",
    "service_url": "https://test-gateway.local:9001",
    "auth_cert_id": 1,
    "sign_cert_id": 2
  }' | python -m json.tool
```

#### READ All Directory Entries
```bash
curl http://localhost:9000/api/global-directory | python -m json.tool
```

#### READ Single Directory Entry
```bash
curl http://localhost:9000/api/global-directory/1 | python -m json.tool
```

#### UPDATE Directory Entry
```bash
curl -X PUT http://localhost:9000/api/global-directory/1 \
  -H "Content-Type: application/json" \
  -d '{
    "service_url": "https://new-gateway.local:9001",
    "status": "ACTIVE"
  }' | python -m json.tool
```

#### DELETE Directory Entry
```bash
curl -X DELETE http://localhost:9000/api/global-directory/1
```

---

## Complete 7-Step Registration Test

Copy and paste these commands sequentially:

### STEP 1: Create Entity

```bash
curl -X POST http://localhost:9000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "TEST_ORG",
    "entity_name": "Test Organization",
    "entity_type": "Organization",
    "status": "ACTIVE"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Entity created",
  "entity_id": 1
}
```

---

### STEP 2: Register Gateway (PENDING)

```bash
curl -X POST http://localhost:9000/api/network-config \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Security Gateway",
    "version": "2.0",
    "network_instance": "TEST",
    "gateway_code": "TEST_GW001",
    "entity_id": 1,
    "host": "192.168.1.100",
    "port": 9001,
    "hostname": "test-gateway.local",
    "ip_address": "192.168.1.100",
    "environment": "Testing"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Gateway registered (PENDING)",
  "id": 1
}
```

---

### STEP 3a: Upload AUTH Public Key

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_type": "AUTH",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ExKG\nLklLbXKOMJAK7wqaGrQSdP7MjLjOpKJPzXpTx+TpjXxCQLpIuJ6rO7CZ9Q5vV8Qm\nWn7xU3ZqZ3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z\n-----END PUBLIC KEY-----"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "AUTH key uploaded",
  "key_id": 1
}
```

---

### STEP 3b: Upload SIGN Public Key

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_type": "SIGN",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx9VTQ5JCQs3wtXKcM9qC\n4x9RJ0L6M2Q1p8C3O9Q9s8vL4xP2U5V6q7s8T3U4Y5Z6a7b8C9d0E1f2G3h4I5j6\nK7l8M9n0O1p2Q3r4S5t6U7v8W9x0Y1z2A3b4C5d6E7f8G9h0I1j2K3l4M5n6O7p8\n-----END PUBLIC KEY-----"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "SIGN key uploaded",
  "key_id": 2
}
```

---

### STEP 4a: Submit AUTH CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCFUExFTATBgNVBAgMDFRlc3RUb3duLlVM\nMRQwEgYDVQQHDAtUZXN0Q291bnRyeTEPMA0GA1UECgwGVGVzdENvMQswCQYDVQQD\nDAJBVTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5\n/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLECAwEAAaA2MDAw\nBgMCABAME1Rlc3RBcC5QbGFjZWhvbGRlcjELBgNVBAwEA1VTQzANBgkqhkiG9w0B\nAQUFAAOCAQEA1Z3VS5JJcds3xfn/ExKGLklLBZqLpV2S7PLD1/Q2\n-----END CERTIFICATE REQUEST-----"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "AUTH CSR submitted (PENDING)",
  "csr_id": 1
}
```

---

### STEP 4b: Submit SIGN CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 2,
    "cert_type": "SIGN",
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCR0ExFTATBgNVBAgMDFRlc3RQcm9WYWxs\nMRQwEgYDVQQHDAtUZXN0U3RhY2tvdmVyMQ8wDQYDVQQKDAZUZXN0Q29YDVAYDVQD\nDAJTRzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5\n/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLExAwaEAwEAAaA2MDAw\nBgMCABAME1Rlc3RBcC5QbGFjZWhvbGRlcjELBgNVBAwEA1VTQzANBgkqhkiG9w0B\nAQUFAAOCAQEA1Z3VS5JJcds3xfn/ExKGLklLBZqLpV2S7PLD1/Q2\n-----END CERTIFICATE REQUEST-----"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "SIGN CSR submitted (PENDING)",
  "csr_id": 2
}
```

---

### STEP 5a: Store AUTH Certificate

```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\nBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\nMIIDBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\n-----END CERTIFICATE-----",
    "issued_by": "Test CA Authority",
    "valid_from": "2026-04-11T10:00:00",
    "valid_to": "2027-04-11T10:00:00"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "AUTH certificate stored (ACTIVE)",
  "cert_id": 1
}
```

---

### STEP 5b: Store SIGN Certificate

```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 2,
    "cert_type": "SIGN",
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDBTCCAe2gAwIBAgIUgKyQaJ9c2M8HxZ8Q5c8L6xQ5678CgKBERYe3EXAMPLE\nBTCCAe2gAwIBAgIUgKyQaJ9c2M8HxZ8Q5c8L6xQ5678CgKBERYe3EXAMPLE\nMIIDBTCCAe2gAwIBAgIUgKyQaJ9c2M8HxZ8Q5c8L6xQ5678CgKBERYe3EXAMPLE\n-----END CERTIFICATE-----",
    "issued_by": "Test CA Authority",
    "valid_from": "2026-04-11T10:01:00",
    "valid_to": "2027-04-11T10:01:00"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "SIGN certificate stored (ACTIVE)",
  "cert_id": 2
}
```

---

### STEP 6: Admin Approval

```bash
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "action": "APPROVED",
    "performed_by": "test_admin@test.com",
    "remarks": "Test gateway verified and approved. All conditions met for production."
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Action logged: APPROVED",
  "log_id": 3
}
```

---

### STEP 7: Publish to Global Directory

```bash
curl -X POST http://localhost:9000/api/global-directory \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "TEST_ORG",
    "gateway_code": "TEST_GW001",
    "service_url": "https://test-gateway.local:9001",
    "auth_cert_id": 1,
    "sign_cert_id": 2
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Published to global directory (ACTIVE)",
  "directory_id": 1
}
```

---

## Verification Commands

After completing all 7 steps, verify everything:

### Verify Gateway Status (Should be APPROVED)

```bash
curl http://localhost:9000/api/network-config/TEST_GW001 | python -m json.tool
```

### Verify Audit Trail (Should show: SUBMITTED, APPROVED)

```bash
curl http://localhost:9000/api/registration-log/gateway/TEST_GW001 | python -m json.tool
```

### Verify CSRs (Should show: SIGNED status)

```bash
curl "http://localhost:9000/api/certificate-requests?status=SIGNED" | python -m json.tool
```

### Verify Certificates (Should show: ACTIVE)

```bash
curl http://localhost:9000/api/certificates/gateway/TEST_GW001 | python -m json.tool
```

### Discover Gateway (Should show in directory)

```bash
curl http://localhost:9000/api/global-directory | python -m json.tool
```

---

## Quick Status Check

```bash
# One command to verify the entire flow
echo "=== Gateway Status ===" && \
curl -s http://localhost:9000/api/network-config/TEST_GW001 | grep -o '"status":"[^"]*"' && \
echo -e "\n=== Certificates ===" && \
curl -s http://localhost:9000/api/certificates/gateway/TEST_GW001 | grep -o '"cert_type":"[^"]*"' && \
echo -e "\n=== Discoverable ===" && \
curl -s http://localhost:9000/api/global-directory | grep '"status"'
```

---

## Common Issues & Solutions

### Issue: "Gateway not APPROVED" error at Step 7

**Solution**: Complete Step 6 (Admin Approval) first
```bash
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","action":"APPROVED","performed_by":"admin@test.com","remarks":"Approved"}'
```

---

### Issue: Duplicate gateway_code error

**Solution**: Use a different gateway_code
```bash
# Change TEST_GW001 to TEST_GW002, TEST_GW003, etc.
```

---

### Issue: Database not configured error

**Solution**: Run the setup commands at the top
```bash
curl -X POST http://localhost:9000/api/save-db-config \
  -H "Content-Type: application/json" \
  -d '{"host":"localhost","port":3306,"username":"root","password":"password","database":"gs1"}'
```

---

## Test Flow as Bash Script

Save this as `test_flow.sh`:

```bash
#!/bin/bash

set -e

echo "🔐 Testing 7-Step Security Server Registration Flow..."

# STEP 1
echo -e "\n[1/7] Creating entity..."
curl -s -X POST http://localhost:9000/api/entities \
  -H "Content-Type: application/json" \
  -d '{"entity_code":"TEST_ORG","entity_name":"Test Org","entity_type":"Organization","status":"ACTIVE"}' > /dev/null
echo "✓ Entity created"

# STEP 2
echo "[2/7] Registering gateway (PENDING)..."
curl -s -X POST http://localhost:9000/api/network-config \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","entity_id":1,"title":"Test Gateway","version":"1.0","network_instance":"TEST","host":"192.168.1.100","port":9001,"hostname":"test.local","ip_address":"192.168.1.100","environment":"Test"}' > /dev/null
echo "✓ Gateway registered (PENDING)"

# STEP 3
echo "[3/7] Uploading keys..."
curl -s -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","key_type":"AUTH","public_key":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"}' > /dev/null
curl -s -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","key_type":"SIGN","public_key":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"}' > /dev/null
echo "✓ Keys uploaded (AUTH, SIGN)"

# STEP 4
echo "[4/7] Submitting CSRs (PENDING)..."
curl -s -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","key_id":1,"cert_type":"AUTH","csr_data":"-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"}' > /dev/null
curl -s -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","key_id":2,"cert_type":"SIGN","csr_data":"-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"}' > /dev/null
echo "✓ CSRs submitted (PENDING)"

# STEP 5
echo "[5/7] Storing certificates (ACTIVE)..."
curl -s -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","key_id":1,"cert_type":"AUTH","certificate":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","issued_by":"Test CA","valid_from":"2026-04-11T10:00:00","valid_to":"2027-04-11T10:00:00"}' > /dev/null
curl -s -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","key_id":2,"cert_type":"SIGN","certificate":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","issued_by":"Test CA","valid_from":"2026-04-11T10:00:00","valid_to":"2027-04-11T10:00:00"}' > /dev/null
echo "✓ Certificates stored (ACTIVE)"

# STEP 6
echo "[6/7] Admin approval (APPROVED)..."
curl -s -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"TEST_GW001","action":"APPROVED","performed_by":"admin@test.com","remarks":"Approved"}' > /dev/null
echo "✓ Gateway approved"

# STEP 7
echo "[7/7] Publishing to directory (ACTIVE)..."
curl -s -X POST http://localhost:9000/api/global-directory \
  -H "Content-Type: application/json" \
  -d '{"entity_code":"TEST_ORG","gateway_code":"TEST_GW001","service_url":"https://test.local:9001","auth_cert_id":1,"sign_cert_id":2}' > /dev/null
echo "✓ Published to directory"

echo -e "\n✅ Complete! Gateway is now DISCOVERABLE"
echo -e "\nVerify:"
echo "curl http://localhost:9000/api/global-directory"
```

Run it:
```bash
chmod +x test_flow.sh
./test_flow.sh
```

---

## CSR Registration Workflow

This is the **actual process** for registering security server certificates with X-Road.

### Prerequisites
1. Security server must be installed and running
2. Gateway must be registered in network_config table
3. Server keys must be generated and stored in server_keys table

### Step 1: Create Server Keys

First, retrieve the key IDs from your security server:

```bash
curl -X GET http://localhost:5000/keys \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Store key information in database:

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_type": "AUTH",
    "public_key": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
  }' | python -m json.tool
```

### Step 2: Generate CSR (on security server)

```bash
# On security server, generate CSR
curl -X POST http://localhost:8080/api/keys/csr \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyId": "KEY_ID_FROM_STEP_1",
    "usage": "AUTHENTICATION"
  }'
```

This returns CSR data. Save it locally.

### Step 3: Register CSR in Database

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": "KEY_ID_FROM_STEP_1",
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "AUTH",
    "status": "PENDING"
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "CSR registered successfully",
  "csr_id": 1
}
```

### Step 4: Submit CSR to CA

```bash
# Send CSR to Certificate Authority
curl -X POST https://ca.x-road.example.com/enroll \
  -H "Content-Type: application/pkcs10" \
  --data-binary @csr_file.pem
```

CA returns signed certificate.

### Step 5: Store Certificate

Once CA returns the signed certificate:

```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": "KEY_ID_FROM_STEP_1",
    "cert_type": "AUTH",
    "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "issued_by": "X-Road CA",
    "valid_from": "2024-01-01T00:00:00Z",
    "valid_to": "2026-01-01T00:00:00Z",
    "status": "ACTIVE"
  }' | python -m json.tool
```

### Step 6: Update CSR Status

Mark the CSR as APPROVED:

```bash
curl -X PUT http://localhost:9000/api/certificate-requests/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "APPROVED"
  }' | python -m json.tool
```

### Step 7: Verify Certificate

```bash
curl http://localhost:9000/api/certificates/1 | python -m json.tool
```

---

## Database Schema Reference

### Entities Table
```sql
CREATE TABLE entities (
  entity_id INT AUTO_INCREMENT PRIMARY KEY,
  entity_code VARCHAR(255) NOT NULL UNIQUE,
  entity_name VARCHAR(255) NOT NULL,
  entity_type VARCHAR(100) NOT NULL,
  status VARCHAR(50) DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Network Config Table
```sql
CREATE TABLE network_config (
  id INT AUTO_INCREMENT PRIMARY KEY,
  gateway_code VARCHAR(255) NOT NULL UNIQUE,
  entity_id INT NOT NULL,
  title VARCHAR(255),
  version VARCHAR(50),
  host VARCHAR(255),
  port INT,
  hostname VARCHAR(255),
  ip_address VARCHAR(255),
  environment VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);
```

### Server Keys Table
```sql
CREATE TABLE server_keys (
  key_id VARCHAR(255) PRIMARY KEY,
  gateway_code VARCHAR(255) NOT NULL,
  key_type VARCHAR(50) NOT NULL,
  public_key LONGTEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
);
```

### Certificate Requests Table
```sql
CREATE TABLE certificate_requests (
  csr_id INT AUTO_INCREMENT PRIMARY KEY,
  gateway_code VARCHAR(255) NOT NULL,
  key_id VARCHAR(255) NOT NULL,
  csr_data LONGTEXT,
  cert_type VARCHAR(50),
  status VARCHAR(50) DEFAULT 'PENDING',
  requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code),
  FOREIGN KEY (key_id) REFERENCES server_keys(key_id)
);
```

### Certificates Table
```sql
CREATE TABLE certificates (
  cert_id INT AUTO_INCREMENT PRIMARY KEY,
  gateway_code VARCHAR(255) NOT NULL,
  key_id VARCHAR(255) NOT NULL,
  cert_type VARCHAR(50),
  certificate LONGTEXT,
  issued_by VARCHAR(255),
  valid_from DATETIME,
  valid_to DATETIME,
  status VARCHAR(50) DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code),
  FOREIGN KEY (key_id) REFERENCES server_keys(key_id)
);
```

### Registration Log Table
```sql
CREATE TABLE registration_log (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  gateway_code VARCHAR(255) NOT NULL,
  action VARCHAR(100),
  performed_by VARCHAR(255),
  remarks TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
);
```

### Global Directory Table
```sql
CREATE TABLE global_directory (
  directory_id INT AUTO_INCREMENT PRIMARY KEY,
  entity_code VARCHAR(255) NOT NULL,
  gateway_code VARCHAR(255) NOT NULL UNIQUE,
  service_url VARCHAR(255),
  auth_cert_id INT,
  sign_cert_id INT,
  status VARCHAR(50) DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (entity_code) REFERENCES entities(entity_code),
  FOREIGN KEY (gateway_code) REFERENCES network_config(gateway_code)
);
```

