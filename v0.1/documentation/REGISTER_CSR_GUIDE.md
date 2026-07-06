# 🔐 Register Security Server CSR to Database

## Prerequisites
You should have already:
1. ✅ Created Entity
2. ✅ Created Network Config (Gateway Registration)
3. ✅ Uploaded Server Keys (AUTH and SIGN)

## Step 1: Get Required Information

### Find gateway_code
```bash
curl http://localhost:9000/api/network-config/{gateway_code}
```

Example response:
```json
{
  "status": "success",
  "config": {
    "id": 1,
    "gateway_code": "TEST_GW001",
    "entity_id": 1,
    ...
  }
}
```

### Find key_id (for AUTH and SIGN)
```bash
curl http://localhost:9000/api/server-keys/gateway/TEST_GW001
```

Example response:
```json
{
  "status": "success",
  "gateway_code": "TEST_GW001",
  "total": 2,
  "keys": [
    {
      "key_id": 1,
      "gateway_code": "TEST_GW001",
      "key_type": "AUTH",
      "created_at": "2026-04-14T10:00:00"
    },
    {
      "key_id": 2,
      "gateway_code": "TEST_GW001",
      "key_type": "SIGN",
      "created_at": "2026-04-14T10:00:00"
    }
  ]
}
```

---

## Step 2: Read CSR File from Security Server

Assuming your security server has CSR files like:
- `auth.csr` - AUTH certificate signing request
- `sign.csr` - SIGN certificate signing request

### Read CSR file (Linux/Mac):
```bash
cat auth.csr
cat sign.csr
```

### Read CSR file (Windows PowerShell):
```powershell
Get-Content auth.csr
Get-Content sign.csr
```

### Expected CSR content format:
```
-----BEGIN CERTIFICATE REQUEST-----
MIICqDCCAZQCAQAwXzELMAkGA1UEBhMCFUExFTATBgNVBAgMDFRlc3RUb3duLlVM
MRQwEgYDVQQHDAtUZXN0Q291bnRyeTEPMA0GA1UECgwGVGVzdENvMQswCQYDVQQD
DAJBVTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5
/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLECAwEAAaA2MDAw
...
-----END CERTIFICATE REQUEST-----
```

---

## Step 3: Register AUTH CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCFUExFTATBgNVBAgMDFRlc3RUb3duLlVM\nMRQwEgYDVQQHDAtUZXN0Q291bnRyeTEPMA0GA1UECgwGVGVzdENvMQswCQYDVQQD\nDAJBVTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5\n/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLECAwEAAaA2MDAw\nBgMCABAME1Rlc3RBcC5QbGFjZWhvbGRlcjELBgNVBAwEA1VTQzANBgkqhkiG9w0B\nAQUFAAOCAQEA1Z3VS5JJcds3xfn/ExKGLklLBZqLpV2S7PLD1/Q2\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "AUTH"
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

## Step 4: Register SIGN CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 2,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCR0ExFTATBgNVBAgMDFRlc3RQcm9WYWxs\nMRQwEgYDVQQHDAtUZXN0U3RhY2tvdmVyMQ8wDQYDVQQKDAZUZXN0Q29YDVAYDVQD\nDAJTRzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5\n/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLExAwaEAwEAAaA2MDAw\nBgMCABAME1Rlc3RBcC5QbGFjZWhvbGRlcjELBgNVBAwEA1VTQzANBgkqhkiG9w0B\nAQUFAAOCAQEA1Z3VS5JJcds3xfn/ExKGLklLBZqLpV2S7PLD1/Q2\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "SIGN"
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

## Step 5: Verify CSRs Registered

### View All CSRs
```bash
curl http://localhost:9000/api/certificate-requests | python -m json.tool
```

### View Pending CSRs Only
```bash
curl "http://localhost:9000/api/certificate-requests?status=PENDING" | python -m json.tool
```

### View Single CSR
```bash
curl http://localhost:9000/api/certificate-requests/1 | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "success",
  "csr": {
    "csr_id": 1,
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "status": "PENDING",
    "requested_at": "2026-04-14T10:30:00"
  }
}
```

---

## Complete CSR Registration Flow (All Steps)

Assuming you have:
- `gateway_code`: TEST_GW001
- `key_id` (AUTH): 1
- `key_id` (SIGN): 2
- CSR files: auth.csr, sign.csr

### Run these in sequence:

```bash
# Register AUTH CSR
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n[PASTE YOUR auth.csr CONTENT HERE]\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "AUTH"
  }'

# Register SIGN CSR
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 2,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n[PASTE YOUR sign.csr CONTENT HERE]\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "SIGN"
  }'

# Verify both CSRs registered
curl "http://localhost:9000/api/certificate-requests?status=PENDING"
```

---

## Database Status After Registration

**certificate_requests table:**
```
csr_id | gateway_code | key_id | cert_type | status
-------|--------------|--------|-----------|--------
1      | TEST_GW001   | 1      | AUTH      | PENDING
2      | TEST_GW001   | 2      | SIGN      | PENDING
```

---

## Next Step: Sign Certificates

Once CSRs are registered, you need to:
1. Send CSRs to CA for signing
2. Get signed certificates back
3. Register certificates via `/api/certificates` endpoint (auth_cert_id and sign_cert_id will be auto-updated to SIGNED)

See `TEST_COMMANDS.md` for certificate registration examples.

