# 🔐 Security Server Registration Flow - Complete API Guide

## Overview

A security server goes through 7 progressive trust stages before becoming discoverable by other systems.

```
STEP 1: Create Entity/Organization
   ↓
STEP 2: Register Security Server (PENDING)
   ↓
STEP 3: Upload AUTH & SIGN Public Keys
   ↓
STEP 4: Submit CSRs to CA
   ↓
STEP 5: Store CA-Signed Certificates
   ↓
STEP 6: Admin Approval (APPROVED)
   ↓
STEP 7: Publish to Global Directory (DISCOVERABLE)
```

---

## Prerequisites

**Database must be configured once:**

```bash
# Save database configuration
curl -X POST http://localhost:9000/api/save-db-config \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "your_password",
    "database": "gs1"
  }'

# Initialize all tables
curl -X POST http://localhost:9000/api/init-db
```

---

## STEP 1: Create Organization/Entity

**Who**: System Administrator  
**Input**: Organization details  
**Output**: `entity_id` (needed for Step 2)  
**Status**: ACTIVE

```bash
curl -X POST http://localhost:9000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "ORG1",
    "entity_name": "My Organization",
    "entity_type": "Organization",
    "status": "ACTIVE"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Entity created",
  "entity_id": 1
}
```

**Save**: `entity_id = 1`, `entity_code = ORG1`

---

## STEP 2: Register Security Server (PENDING)

**Who**: Security Server Administrator  
**Input**: Server details, entity_id from Step 1  
**Output**: Gateway registered but **PENDING** approval  
**Auto-Action**: Creates log entry "SUBMITTED"  
**Status**: PENDING

```bash
curl -X POST http://localhost:9000/api/network-config \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Security Gateway - Production",
    "version": "1.0",
    "network_instance": "PROD",
    "gateway_code": "GW001",
    "entity_id": 1,
    "host": "192.168.1.100",
    "port": 9001,
    "hostname": "gateway1.example.com",
    "ip_address": "192.168.1.100",
    "environment": "Production"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Gateway registered (PENDING)",
  "id": 1
}
```

**Verify**: Check registration log was auto-created
```bash
curl http://localhost:9000/api/registration-log/gateway/GW001
```

**Save**: `gateway_code = GW001`

---

## STEP 3: Upload AUTH & SIGN Public Keys

**Who**: Security Server  
**Input**: Two public keys (AUTH for TLS, SIGN for message signing)  
**Output**: `key_id` values  
**Status**: Keys stored and ready for CSR submission

### 3a. Upload AUTH Public Key

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_type": "AUTH",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/\nExKGLklLbXKOMJAK7wqaGrQSdP7MjLjOpKJPzXpTx+EXAMPLE\n-----END PUBLIC KEY-----"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "AUTH key uploaded",
  "key_id": 1
}
```

**Save**: `auth_key_id = 1`

### 3b. Upload SIGN Public Key

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_type": "SIGN",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2x9VTQ5JCQs3EXAMPLE\n-----END PUBLIC KEY-----"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "SIGN key uploaded",
  "key_id": 2
}
```

**Save**: `sign_key_id = 2`

---

## STEP 4: Submit CSRs (Certificate Signing Requests)

**Who**: Security Server  
**Input**: CSR data (generated locally by security server), key_ids from Step 3  
**Output**: CSRs stored with status "PENDING"  
**Status**: PENDING - waiting for CA to sign

### 4a. Submit AUTH CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 1,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCURUxFTATBgNVBAgMDFN0YWNrc291cmNl\nMRQwEgYDVQQHDAtTdGFja292ZXJmbG93MQ8wDQYDVQQKDAZDb3VudHJ5MQswCQYD\nVQQDDAJTRzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHb\nN8X5/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLE=\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "AUTH"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "AUTH CSR submitted (PENDING)",
  "csr_id": 1
}
```

**Save**: `auth_csr_id = 1`

### 4b. Submit SIGN CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 2,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCRUExFTATBgNVBAgMDFN0YWNrc291cmNl\nMRQwEgYDVQQHDAtTdGFja292ZXJmbG93MQ8wDQYDVQQKDAZDb3VudHJ5MQswCQYD\nVQQDDAJDQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHb\nN8X5/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLE=\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "SIGN"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "SIGN CSR submitted (PENDING)",
  "csr_id": 2
}
```

**Save**: `sign_csr_id = 2`

**Verify pending CSRs:**
```bash
curl "http://localhost:9000/api/certificate-requests?status=PENDING"
```

---

## STEP 5: Store CA-Signed Certificates

**Who**: CA Service (or Administrator on behalf of CA)  
**Input**: Signed certificates from CA, valid dates  
**Output**: Certificates stored with status "ACTIVE"  
**Auto-Action**: CSR status auto-updated to "SIGNED"  
**Status**: ACTIVE

### 5a. Store AUTH Certificate

```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\nMIIDBTCCAe2gAwIBAgIUfKxPaJ9c2M7HxZ8Q5c8L6xQ1234CgKBERYe3EXAMPLE\n-----END CERTIFICATE-----",
    "issued_by": "GlobalCA Authority",
    "valid_from": "2026-04-11T10:00:00",
    "valid_to": "2027-04-11T10:00:00"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "AUTH certificate stored (ACTIVE)",
  "cert_id": 1
}
```

**Save**: `auth_cert_id = 1`

### 5b. Store SIGN Certificate

```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 2,
    "cert_type": "SIGN",
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDBTCCAe2gAwIBAgIUgKyQaJ9c2M8HxZ8Q5c8L6xQ5678CgKBERYe3EXAMPLE\nMIIDBTCCAe2gAwIBAgIUgKyQaJ9c2M8HxZ8Q5c8L6xQ5678CgKBERYe3EXAMPLE\n-----END CERTIFICATE-----",
    "issued_by": "GlobalCA Authority",
    "valid_from": "2026-04-11T10:01:00",
    "valid_to": "2027-04-11T10:01:00"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "SIGN certificate stored (ACTIVE)",
  "cert_id": 2
}
```

**Save**: `sign_cert_id = 2`

**Verify** CSRs now show SIGNED status:
```bash
curl "http://localhost:9000/api/certificate-requests?status=SIGNED"
```

**Verify** certificates are ACTIVE:
```bash
curl http://localhost:9000/api/certificates/gateway/GW001
```

---

## STEP 6: Admin Approval

**Who**: System Administrator  
**Input**: Approval decision (APPROVED or REJECTED)  
**Auto-Action**: network_config status auto-updated to APPROVED/REJECTED  
**Status**: APPROVED (now eligible for directory publication)

```bash
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "action": "APPROVED",
    "performed_by": "admin@example.com",
    "remarks": "Security gateway verified and approved for production use. Both AUTH and SIGN certificates validated."
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Action logged: APPROVED",
  "log_id": 3
}
```

**Verify** gateway status is now APPROVED:
```bash
curl http://localhost:9000/api/network-config/GW001
```

**Verify** complete audit trail:
```bash
curl http://localhost:9000/api/registration-log/gateway/GW001
```

---

## STEP 7: Publish to Global Directory (DISCOVERABLE)

**Who**: System Administrator  
**Prerequisite**: ⚠️ Gateway must be APPROVED first (Step 6)  
**Input**: Certificate IDs from Step 5, service URL  
**Output**: Gateway published with status "ACTIVE"  
**Status**: ACTIVE - **NOW DISCOVERABLE BY OTHER SYSTEMS**

```bash
curl -X POST http://localhost:9000/api/global-directory \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "ORG1",
    "gateway_code": "GW001",
    "service_url": "https://gateway1.example.com:9001",
    "auth_cert_id": 1,
    "sign_cert_id": 2
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Published to global directory (ACTIVE)",
  "directory_id": 1
}
```

**Verify** gateway is now discoverable:
```bash
curl http://localhost:9000/api/global-directory
```

**Response:**
```json
{
  "status": "success",
  "message": "Global Directory",
  "total": 1,
  "directory": [
    {
      "directory_id": 1,
      "entity_code": "ORG1",
      "gateway_code": "GW001",
      "entity_name": "My Organization",
      "host": "192.168.1.100",
      "port": 9001,
      "service_url": "https://gateway1.example.com:9001",
      "status": "ACTIVE",
      "created_at": "2026-04-11T10:30:00"
    }
  ]
}
```

---

## Complete Flow - All Steps Combined

```bash
#!/bin/bash
echo "=== STEP 1: Create Organization ==="
ENTITY=$(curl -s -X POST http://localhost:9000/api/entities \
  -H "Content-Type: application/json" \
  -d '{"entity_code":"ORG1","entity_name":"My Organization","entity_type":"Organization","status":"ACTIVE"}')
ENTITY_ID=$(echo $ENTITY | grep -o '"entity_id":[0-9]*' | cut -d':' -f2)
echo "Entity ID: $ENTITY_ID"

echo -e "\n=== STEP 2: Register Security Gateway (PENDING) ==="
GATEWAY=$(curl -s -X POST http://localhost:9000/api/network-config \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Security Gateway","version":"1.0","network_instance":"PROD",
    "gateway_code":"GW001","entity_id":'$ENTITY_ID',"host":"192.168.1.100",
    "port":9001,"hostname":"gateway1.example.com","ip_address":"192.168.1.100",
    "environment":"Production"
  }')
echo "Gateway registered with status PENDING"

echo -e "\n=== STEP 3: Upload AUTH Key ==="
AUTH_KEY=$(curl -s -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"GW001","key_type":"AUTH","public_key":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"}')
AUTH_KEY_ID=$(echo $AUTH_KEY | grep -o '"key_id":[0-9]*' | cut -d':' -f2)
echo "AUTH Key ID: $AUTH_KEY_ID"

echo -e "\n=== STEP 3: Upload SIGN Key ==="
SIGN_KEY=$(curl -s -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"GW001","key_type":"SIGN","public_key":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"}')
SIGN_KEY_ID=$(echo $SIGN_KEY | grep -o '"key_id":[0-9]*' | cut -d':' -f2 | tail -1)
echo "SIGN Key ID: $SIGN_KEY_ID"

echo -e "\n=== STEP 4: Submit AUTH CSR ==="
curl -s -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"GW001","key_id":'$AUTH_KEY_ID',"cert_type":"AUTH","csr_data":"-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"}'
echo "AUTH CSR submitted (PENDING)"

echo -e "\n=== STEP 4: Submit SIGN CSR ==="
curl -s -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"GW001","key_id":'$SIGN_KEY_ID',"cert_type":"SIGN","csr_data":"-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"}'
echo "SIGN CSR submitted (PENDING)"

echo -e "\n=== STEP 5: Store AUTH Certificate ==="
AUTH_CERT=$(curl -s -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"GW001","key_id":'$AUTH_KEY_ID',"cert_type":"AUTH","certificate":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","issued_by":"GlobalCA","valid_from":"2026-04-11T10:00:00","valid_to":"2027-04-11T10:00:00"}')
AUTH_CERT_ID=$(echo $AUTH_CERT | grep -o '"cert_id":[0-9]*' | cut -d':' -f2)
echo "AUTH Certificate ID: $AUTH_CERT_ID (ACTIVE)"

echo -e "\n=== STEP 5: Store SIGN Certificate ==="
SIGN_CERT=$(curl -s -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"GW001","key_id":'$SIGN_KEY_ID',"cert_type":"SIGN","certificate":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----","issued_by":"GlobalCA","valid_from":"2026-04-11T10:01:00","valid_to":"2027-04-11T10:01:00"}')
SIGN_CERT_ID=$(echo $SIGN_CERT | grep -o '"cert_id":[0-9]*' | cut -d':' -f2 | tail -1)
echo "SIGN Certificate ID: $SIGN_CERT_ID (ACTIVE)"

echo -e "\n=== STEP 6: Admin Approval ==="
curl -s -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{"gateway_code":"GW001","action":"APPROVED","performed_by":"admin@example.com","remarks":"Approved for production"}'
echo "Gateway status updated to APPROVED"

echo -e "\n=== STEP 7: Publish to Global Directory ==="
curl -s -X POST http://localhost:9000/api/global-directory \
  -H "Content-Type: application/json" \
  -d '{"entity_code":"ORG1","gateway_code":"GW001","service_url":"https://gateway1.example.com:9001","auth_cert_id":'$AUTH_CERT_ID',"sign_cert_id":'$SIGN_CERT_ID'}'
echo "Gateway published (DISCOVERABLE)"

echo -e "\n=== Verify Discovery ==="
curl -s http://localhost:9000/api/global-directory | head -20
```

---

## Status Progression

```
Step 1: entity.status = ACTIVE

Step 2: network_config.status = PENDING
        ↓ (auto-log SUBMITTED)

Step 3: server_keys created (AUTH + SIGN)

Step 4: certificate_requests.status = PENDING (x2)

Step 5: certificates.status = ACTIVE (x2)
        ↓ (auto-update CSRs to SIGNED)

Step 6: network_config.status = APPROVED
        ↓ (auto-updated by log action)

Step 7: global_directory.status = ACTIVE
        ✅ NOW DISCOVERABLE
```

---

## Key Points

✅ **Each step must be completed in order**
✅ **STEP 6 approval is required before STEP 7 publication**
✅ **Auto-actions** maintain data consistency
✅ **Audit trail** preserved throughout (see registration_log)
✅ **Both** AUTH and SIGN certificates required
✅ **Global directory** enables system-wide discovery

---

## Query Discovery

```bash
# List all pending servers (PENDING status)
curl http://localhost:9000/api/network-config

# List approved servers (APPROVED status)
curl "http://localhost:9000/api/network-config" | grep APPROVED

# List discoverable servers (ACTIVE in directory)
curl http://localhost:9000/api/global-directory

# View audit trail for specific gateway
curl http://localhost:9000/api/registration-log/gateway/GW001

# View all certificates for gateway
curl http://localhost:9000/api/certificates/gateway/GW001
```

