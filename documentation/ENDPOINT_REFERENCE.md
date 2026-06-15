# 📋 Complete Endpoint Reference - All HTTP Methods

## Database Configuration (3 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/save-db-config` | Save database credentials |
| POST | `/api/test-connection` | Test database connection |
| POST | `/api/init-db` | Initialize all 7 tables |

---

## TABLE 1: ENTITIES (5 endpoints)

| Method | Endpoint | Purpose | Example |
|--------|----------|---------|---------|
| **POST** | `/api/entities` | Create new entity | `curl -X POST http://localhost:9000/api/entities -d '{"entity_code":"ORG1",...}'` |
| **GET** | `/api/entities` | Get all entities | `curl http://localhost:9000/api/entities` |
| **GET** | `/api/entities/{entity_id}` | Get specific entity | `curl http://localhost:9000/api/entities/1` |
| **PUT** | `/api/entities/{entity_id}` | Update entity | `curl -X PUT http://localhost:9000/api/entities/1 -d '{"entity_name":"Updated"}'` |
| **DELETE** | `/api/entities/{entity_id}` | Delete entity | `curl -X DELETE http://localhost:9000/api/entities/1` |

---

## TABLE 2: NETWORK_CONFIG (5 endpoints)

| Method | Endpoint | Purpose | Status Auto-Action |
|--------|----------|---------|-------------------|
| **POST** | `/api/network-config` | Register gateway (PENDING) | ✅ Logs SUBMITTED |
| **GET** | `/api/network-config` | Get all gateways | - |
| **GET** | `/api/network-config/{gateway_code}` | Get specific gateway | - |
| **PUT** | `/api/network-config/{gateway_code}` | Update gateway | - |
| **DELETE** | `/api/network-config/{gateway_code}` | Delete gateway | - |

**Example:**
```bash
POST /api/network-config
{
  "gateway_code": "GW001",
  "entity_id": 1,
  "title": "Security Gateway 1",
  ...
}
```

---

## TABLE 3: SERVER_KEYS (6 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **POST** | `/api/server-keys` | Upload public key (AUTH or SIGN) |
| **GET** | `/api/server-keys` | Get all keys |
| **GET** | `/api/server-keys/{key_id}` | Get specific key |
| **GET** | `/api/server-keys/gateway/{gateway_code}` | Get all keys for gateway |
| **PUT** | `/api/server-keys/{key_id}` | Update key |
| **DELETE** | `/api/server-keys/{key_id}` | Delete key |

**Upload Example:**
```bash
POST /api/server-keys
{
  "gateway_code": "GW001",
  "key_type": "AUTH",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
}
```

---

## TABLE 4: CERTIFICATE_REQUESTS (5 endpoints)

| Method | Endpoint | Purpose | Filtering |
|--------|----------|---------|-----------|
| **POST** | `/api/certificate-requests` | Submit CSR (PENDING) | Status: PENDING |
| **GET** | `/api/certificate-requests` | Get all CSRs | ?status=PENDING/SIGNED/REJECTED |
| **GET** | `/api/certificate-requests/{csr_id}` | Get specific CSR | - |
| **PUT** | `/api/certificate-requests/{csr_id}` | Update CSR status | - |
| **DELETE** | `/api/certificate-requests/{csr_id}` | Delete CSR | - |

**Submit CSR Example:**
```bash
POST /api/certificate-requests
{
  "gateway_code": "GW001",
  "key_id": 1,
  "cert_type": "AUTH",
  "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"
}
```

**List Pending CSRs:**
```bash
GET /api/certificate-requests?status=PENDING
```

---

## TABLE 5: CERTIFICATES (6 endpoints)

| Method | Endpoint | Purpose | Auto-Action |
|--------|----------|---------|-------------|
| **POST** | `/api/certificates` | Store signed certificate (ACTIVE) | ✅ Updates CSR to SIGNED |
| **GET** | `/api/certificates` | Get all certificates | - |
| **GET** | `/api/certificates/{cert_id}` | Get specific certificate | - |
| **GET** | `/api/certificates/gateway/{gateway_code}` | Get certificates for gateway | - |
| **PUT** | `/api/certificates/{cert_id}` | Update certificate status | - |
| **DELETE** | `/api/certificates/{cert_id}` | Delete certificate | - |

**Store Certificate Example:**
```bash
POST /api/certificates
{
  "gateway_code": "GW001",
  "key_id": 1,
  "cert_type": "AUTH",
  "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
  "issued_by": "CA Authority",
  "valid_from": "2026-04-10T10:20:00",
  "valid_to": "2027-04-10T10:20:00"
}
```

---

## TABLE 6: REGISTRATION_LOG (6 endpoints)

| Method | Endpoint | Purpose | Auto-Action |
|--------|----------|---------|-------------|
| **POST** | `/api/registration-log` | Log action (SUBMITTED/APPROVED/REJECTED) | ✅ Updates network_config status |
| **GET** | `/api/registration-log` | Get all logs | ?action=SUBMITTED/APPROVED/REJECTED |
| **GET** | `/api/registration-log/{log_id}` | Get specific log | - |
| **GET** | `/api/registration-log/gateway/{gateway_code}` | Get audit trail for gateway | - |
| **PUT** | `/api/registration-log/{log_id}` | Update log entry | - |
| **DELETE** | `/api/registration-log/{log_id}` | Delete log entry | - |

**Approve Gateway Example:**
```bash
POST /api/registration-log
{
  "gateway_code": "GW001",
  "action": "APPROVED",
  "performed_by": "admin@example.com",
  "remarks": "Gateway verified and approved"
}
```

**View Audit Trail:**
```bash
GET /api/registration-log/gateway/GW001
```

---

## TABLE 7: GLOBAL_DIRECTORY (5 endpoints)

| Method | Endpoint | Purpose | Requirement |
|--------|----------|---------|-------------|
| **POST** | `/api/global-directory` | Publish to directory (ACTIVE) | ⚠️ Requires status=APPROVED |
| **GET** | `/api/global-directory` | Discover all servers | ?status=ACTIVE/INACTIVE |
| **GET** | `/api/global-directory/{directory_id}` | Get specific entry | - |
| **PUT** | `/api/global-directory/{directory_id}` | Update directory entry | - |
| **DELETE** | `/api/global-directory/{directory_id}` | Remove from directory | - |

**Publish to Directory Example:**
```bash
POST /api/global-directory
{
  "entity_code": "ORG1",
  "gateway_code": "GW001",
  "service_url": "https://gateway1.example.com:9001",
  "auth_cert_id": 1,
  "sign_cert_id": 2
}
```

**Discover All Published Servers:**
```bash
GET /api/global-directory
```

**Discover Only Active Servers:**
```bash
GET /api/global-directory?status=ACTIVE
```

---

## ENDPOINT SUMMARY

```
Total Endpoints: 41

Database Setup:        3 endpoints
├─ Configuration:      POST, POST, POST

Entities:             5 endpoints
├─ CRUD:              POST, GET, GET/:id, PUT/:id, DELETE/:id

Network Config:       5 endpoints
├─ CRUD:              POST, GET, GET/:code, PUT/:code, DELETE/:code

Server Keys:          6 endpoints
├─ CRUD:              POST, GET, GET/:id, PUT/:id, DELETE/:id
├─ Extra:             GET/gateway/:code

Certificate Requests: 5 endpoints
├─ CRUD:              POST, GET, GET/:id, PUT/:id, DELETE/:id
├─ Filtering:         ?status=PENDING

Certificates:         6 endpoints
├─ CRUD:              POST, GET, GET/:id, PUT/:id, DELETE/:id
├─ Extra:             GET/gateway/:code

Registration Log:     6 endpoints
├─ CRUD:              POST, GET, GET/:id, PUT/:id, DELETE/:id
├─ Extra:             GET/gateway/:code
├─ Filtering:         ?action=APPROVED

Global Directory:     5 endpoints
├─ CRUD:              POST, GET, GET/:id, PUT/:id, DELETE/:id
├─ Filtering:         ?status=ACTIVE
```

---

## HTTP Methods Used

| Method | Purpose | How Often |
|--------|---------|-----------|
| **GET** | Read data | 17 times |
| **POST** | Create data | 7 times |
| **PUT** | Update data | 7 times |
| **DELETE** | Delete data | 7 times |

---

## Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | Success | ✅ Record created/updated/retrieved |
| **404** | Not Found | ❌ Record doesn't exist |
| **400** | Bad Request | ❌ Invalid input or validation error |
| **409** | Conflict | ❌ Duplicate key or constraint violation |
| **500** | Server Error | ❌ Database connection or processing error |

---

## Request/Response Format

### Standard Create Request
```json
POST /api/{table}
{
  "field1": "value1",
  "field2": "value2"
}
```

### Standard Create Response
```json
{
  "status": "success",
  "message": "Resource created",
  "resource_id": 1
}
```

### Standard Read Response
```json
{
  "status": "success",
  "total": 10,
  "{resources}": [
    { "id": 1, ... },
    { "id": 2, ... }
  ]
}
```

### Standard Update Request
```json
PUT /api/{table}/{id}
{
  "field_to_update": "new_value"
}
```

### Standard Delete Response
```json
{
  "status": "success",
  "message": "Resource deleted"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Complete Flow with All CRUD Operations

```
1. CREATE entity
   ↓
2. CREATE network-config (auto-logs SUBMITTED)
   ↓
3. CREATE server-keys (x2: AUTH + SIGN)
   ↓
4. CREATE certificate-requests (x2: AUTH + SIGN)
   ↓
5. CREATE certificates (x2, auto-updates CSRs to SIGNED)
   ↓
6. CREATE registration-log (APPROVED, auto-updates config status)
   ↓
7. CREATE global-directory (now published)
   ↓
READ: Discover all published servers
READ: View audit trail for specific gateway
UPDATE: Change gateway settings
UPDATE: Change certificate status
UPDATE: Change directory entry
DELETE: Remove resources if needed
```

---

## Testing with cURL (Ready-to-Use Commands)

```bash
# Create
curl -X POST http://localhost:9000/api/entities -H "Content-Type: application/json" -d '{"entity_code":"ORG1","entity_name":"My Org","entity_type":"Org","status":"ACTIVE"}'

# Read All
curl http://localhost:9000/api/entities

# Read One
curl http://localhost:9000/api/entities/1

# Update
curl -X PUT http://localhost:9000/api/entities/1 -H "Content-Type: application/json" -d '{"entity_name":"Updated Name"}'

# Delete
curl -X DELETE http://localhost:9000/api/entities/1

# Filter
curl "http://localhost:9000/api/certificate-requests?status=PENDING"

# Get by Gateway
curl http://localhost:9000/api/server-keys/gateway/GW001
```

---

## Version Information

- **Backend**: FastAPI 0.104+
- **Database**: MySQL 8.0+
- **Python**: 3.9+
- **Implementation**: v2.0 - Full CRUD for all 7 tables
- **Endpoints**: 41 total
- **Status**: Production Ready ✅

