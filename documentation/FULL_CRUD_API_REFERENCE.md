# 🟢 Complete CRUD Operations - All 7 Tables

## Table of Contents
1. [ENTITIES](#1-entities-crud)
2. [NETWORK_CONFIG](#2-network_config-crud)
3. [SERVER_KEYS](#3-server_keys-crud)
4. [CERTIFICATE_REQUESTS](#4-certificate_requests-crud)
5. [CERTIFICATES](#5-certificates-crud)
6. [REGISTRATION_LOG](#6-registration_log-crud)
7. [GLOBAL_DIRECTORY](#7-global_directory-crud)

---

## 1. ENTITIES CRUD

**Table**: Organizations/entities registering security servers

### CREATE - Add New Entity

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

### READ - Get All Entities

```bash
curl http://localhost:9000/api/entities
```

**Response:**
```json
{
  "status": "success",
  "total": 1,
  "entities": [
    {
      "entity_id": 1,
      "entity_code": "ORG1",
      "entity_name": "My Organization",
      "entity_type": "Organization",
      "status": "ACTIVE",
      "created_at": "2026-04-10T10:00:00"
    }
  ]
}
```

### READ - Get Specific Entity

```bash
curl http://localhost:9000/api/entities/1
```

### UPDATE - Modify Entity

```bash
curl -X PUT http://localhost:9000/api/entities/1 \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "ORG1",
    "entity_name": "Updated Organization Name",
    "entity_type": "Organization",
    "status": "ACTIVE"
  }'
```

### DELETE - Remove Entity

```bash
curl -X DELETE http://localhost:9000/api/entities/1
```

---

## 2. NETWORK_CONFIG CRUD

**Table**: Security server registrations with progressive trust status

### CREATE - Register Gateway (PENDING)

```bash
curl -X POST http://localhost:9000/api/network-config \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Security Gateway 1",
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

**Note**: Auto-logs SUBMITTED event to registration_log

**Response:**
```json
{
  "status": "success",
  "message": "Gateway registered (PENDING)",
  "id": 1
}
```

### READ - Get All Gateways

```bash
curl http://localhost:9000/api/network-config
```

### READ - Get Specific Gateway

```bash
curl http://localhost:9000/api/network-config/GW001
```

### UPDATE - Modify Gateway

```bash
curl -X PUT http://localhost:9000/api/network-config/GW001 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "environment": "Staging"
  }'
```

### DELETE - Remove Gateway

```bash
curl -X DELETE http://localhost:9000/api/network-config/GW001
```

---

## 3. SERVER_KEYS CRUD

**Table**: AUTH & SIGN public keys per gateway

### CREATE - Upload Public Key

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_type": "AUTH",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
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

### READ - Get All Keys

```bash
curl http://localhost:9000/api/server-keys
```

### READ - Get Specific Key

```bash
curl http://localhost:9000/api/server-keys/1
```

### READ - Get All Keys for Gateway

```bash
curl http://localhost:9000/api/server-keys/gateway/GW001
```

### UPDATE - Replace Key

```bash
curl -X PUT http://localhost:9000/api/server-keys/1 \
  -H "Content-Type: application/json" \
  -d '{
    "public_key": "-----BEGIN PUBLIC KEY-----\n[new key content]\n-----END PUBLIC KEY-----"
  }'
```

### DELETE - Remove Key

```bash
curl -X DELETE http://localhost:9000/api/server-keys/1
```

---

## 4. CERTIFICATE_REQUESTS CRUD

**Table**: CSR submissions for CA signing (PENDING → SIGNED)

### CREATE - Submit CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 1,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCVVM...\n-----END CERTIFICATE REQUEST-----",
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

### READ - Get All CSRs

```bash
curl http://localhost:9000/api/certificate-requests
```

### READ - Get Pending CSRs Only

```bash
curl "http://localhost:9000/api/certificate-requests?status=PENDING"
```

### READ - Get Specific CSR

```bash
curl http://localhost:9000/api/certificate-requests/1
```

### UPDATE - Change CSR Status

```bash
curl -X PUT http://localhost:9000/api/certificate-requests/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "SIGNED"
  }'
```

### DELETE - Remove CSR

```bash
curl -X DELETE http://localhost:9000/api/certificate-requests/1
```

---

## 5. CERTIFICATES CRUD

**Table**: Signed certificates from CA (ACTIVE, EXPIRED, REVOKED)

### CREATE - Store Signed Certificate

```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDBTCCAe2gAwIBAgIUfKxPaJ9c2M7...\n-----END CERTIFICATE-----",
    "issued_by": "CA Authority",
    "valid_from": "2026-04-10T10:20:00",
    "valid_to": "2027-04-10T10:20:00"
  }'
```

**Note**: Auto-updates corresponding CSR status to SIGNED

**Response:**
```json
{
  "status": "success",
  "message": "AUTH certificate stored (ACTIVE)",
  "cert_id": 1
}
```

### READ - Get All Certificates

```bash
curl http://localhost:9000/api/certificates
```

### READ - Get Specific Certificate

```bash
curl http://localhost:9000/api/certificates/1
```

### READ - Get All Certificates for Gateway

```bash
curl http://localhost:9000/api/certificates/gateway/GW001
```

### UPDATE - Change Certificate Status

```bash
curl -X PUT http://localhost:9000/api/certificates/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "REVOKED"
  }'
```

### DELETE - Remove Certificate

```bash
curl -X DELETE http://localhost:9000/api/certificates/1
```

---

## 6. REGISTRATION_LOG CRUD

**Table**: Audit trail of registration actions (SUBMITTED, APPROVED, REJECTED)

### CREATE - Log Action

```bash
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "action": "APPROVED",
    "performed_by": "admin@example.com",
    "remarks": "Gateway verified and approved for production"
  }'
```

**Note**: Auto-updates network_config.status to APPROVED/REJECTED

**Response:**
```json
{
  "status": "success",
  "message": "Action logged: APPROVED",
  "log_id": 1
}
```

### READ - Get All Logs

```bash
curl http://localhost:9000/api/registration-log
```

### READ - Get Logs with Specific Action

```bash
curl "http://localhost:9000/api/registration-log?action=APPROVED"
```

### READ - Get Specific Log Entry

```bash
curl http://localhost:9000/api/registration-log/1
```

### READ - Get Audit Trail for Gateway

```bash
curl http://localhost:9000/api/registration-log/gateway/GW001
```

### UPDATE - Modify Log Entry

```bash
curl -X PUT http://localhost:9000/api/registration-log/1 \
  -H "Content-Type: application/json" \
  -d '{
    "action": "APPROVED",
    "remarks": "Updated remarks"
  }'
```

### DELETE - Remove Log Entry

```bash
curl -X DELETE http://localhost:9000/api/registration-log/1
```

---

## 7. GLOBAL_DIRECTORY CRUD

**Table**: Published discoverable servers (requires APPROVED status first)

### CREATE - Publish to Directory

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

**Note**: ⚠️ Requires network_config.status = APPROVED

**Response:**
```json
{
  "status": "success",
  "message": "Published to global directory (ACTIVE)",
  "directory_id": 1
}
```

### READ - Get All Published Servers

```bash
curl http://localhost:9000/api/global-directory
```

### READ - Get Only Active Servers

```bash
curl "http://localhost:9000/api/global-directory?status=ACTIVE"
```

### READ - Get Specific Directory Entry

```bash
curl http://localhost:9000/api/global-directory/1
```

### UPDATE - Modify Directory Entry

```bash
curl -X PUT http://localhost:9000/api/global-directory/1 \
  -H "Content-Type: application/json" \
  -d '{
    "service_url": "https://new-gateway1.example.com:9001",
    "status": "INACTIVE"
  }'
```

### DELETE - Remove from Directory

```bash
curl -X DELETE http://localhost:9000/api/global-directory/1
```

---

## Quick Reference Table

| Table | CREATE | READ | UPDATE | DELETE |
|-------|--------|------|--------|--------|
| **ENTITIES** | ✅ POST `/api/entities` | ✅ GET `/api/entities` | ✅ PUT `/api/entities/{id}` | ✅ DEL `/api/entities/{id}` |
| **NETWORK_CONFIG** | ✅ POST `/api/network-config` | ✅ GET `/api/network-config` | ✅ PUT `/api/network-config/{code}` | ✅ DEL `/api/network-config/{code}` |
| **SERVER_KEYS** | ✅ POST `/api/server-keys` | ✅ GET `/api/server-keys` | ✅ PUT `/api/server-keys/{id}` | ✅ DEL `/api/server-keys/{id}` |
| **CERTIFICATE_REQUESTS** | ✅ POST `/api/certificate-requests` | ✅ GET `/api/certificate-requests` | ✅ PUT `/api/certificate-requests/{id}` | ✅ DEL `/api/certificate-requests/{id}` |
| **CERTIFICATES** | ✅ POST `/api/certificates` | ✅ GET `/api/certificates` | ✅ PUT `/api/certificates/{id}` | ✅ DEL `/api/certificates/{id}` |
| **REGISTRATION_LOG** | ✅ POST `/api/registration-log` | ✅ GET `/api/registration-log` | ✅ PUT `/api/registration-log/{id}` | ✅ DEL `/api/registration-log/{id}` |
| **GLOBAL_DIRECTORY** | ✅ POST `/api/global-directory` | ✅ GET `/api/global-directory` | ✅ PUT `/api/global-directory/{id}` | ✅ DEL `/api/global-directory/{id}` |

---

## Additional Query Parameters

### Filter by Status
- `GET /api/certificate-requests?status=PENDING`
- `GET /api/registration-log?action=APPROVED`
- `GET /api/global-directory?status=ACTIVE`

### Get by Gateway Code
- `GET /api/network-config/GW001`
- `GET /api/server-keys/gateway/GW001`
- `GET /api/certificates/gateway/GW001`
- `GET /api/registration-log/gateway/GW001`

---

## Error Responses

```json
{
  "detail": "Error message describing the issue"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad request or validation error
- `404` - Resource not found
- `409` - Conflict (e.g., duplicate gateway_code)
- `500` - Server/database error

---

## Database Schema Reference

| Table | Columns | Key Status | Auto-Generated |
|-------|---------|-----------|------------------|
| **entities** | entity_id, entity_code, entity_name, entity_type, status | entity_code (UNIQUE) | entity_id (PK) |
| **network_config** | id, gateway_code, entity_id, host, port, status | gateway_code (UNIQUE), entity_id (FK) | id (PK) |
| **server_keys** | key_id, gateway_code, key_type, public_key | (gateway_code, key_type) UNIQUE | key_id (PK) |
| **certificate_requests** | csr_id, gateway_code, key_id, csr_data, cert_type, status | gateway_code (FK), key_id (FK) | csr_id (PK) |
| **certificates** | cert_id, gateway_code, key_id, cert_type, certificate, status | gateway_code (FK), key_id (FK) | cert_id (PK) |
| **registration_log** | log_id, gateway_code, action, performed_by, remarks | gateway_code (FK) | log_id (PK) |
| **global_directory** | directory_id, entity_code, gateway_code, service_url, status | gateway_code (FK UNIQUE) | directory_id (PK) |

---

## Complete 7-Step Registration with CRUD

```bash
# 1. CREATE entity
POST /api/entities → entity_id: 1

# 2. CREATE network-config (PENDING)
POST /api/network-config → id: 1

# 3. CREATE server-keys (x2)
POST /api/server-keys (AUTH) → key_id: 1
POST /api/server-keys (SIGN) → key_id: 2

# 4. CREATE certificate-requests (x2, PENDING)
POST /api/certificate-requests (AUTH) → csr_id: 1
POST /api/certificate-requests (SIGN) → csr_id: 2

# 5. CREATE certificates (x2, ACTIVE)
POST /api/certificates (AUTH) → cert_id: 1 [auto-updates CSR to SIGNED]
POST /api/certificates (SIGN) → cert_id: 2 [auto-updates CSR to SIGNED]

# 6. CREATE registration-log (action: APPROVED)
POST /api/registration-log → log_id: 1 [auto-updates config status to APPROVED]

# 7. CREATE global-directory (requires APPROVED)
POST /api/global-directory → directory_id: 1 [now DISCOVERABLE]

# Additional Operations:
GET /api/global-directory → discover all published servers
GET /api/registration-log/gateway/GW001 → view audit trail
```

---

## CRUD Operations Summary

✅ **All 7 tables have complete CRUD coverage:**
- **CREATE** - Add new records
- **READ** - List all, filter by criteria, get specific records
- **UPDATE** - Modify existing records
- **DELETE** - Remove records

✅ **Auto-actions:**
- CREATE network-config → auto-logs SUBMITTED
- CREATE certificates → auto-updates CSR to SIGNED
- CREATE registration-log → auto-updates network-config status

✅ **Validation:**
- UNIQUE constraints on entity_code, gateway_code
- FOREIGN KEY constraints for data integrity
- Status validation (gateway must be APPROVED before publishing)

