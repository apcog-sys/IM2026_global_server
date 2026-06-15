# API Request Quick Reference

## Security Server Registration Workflow

### 1️⃣ REQUEST CERTIFICATES

**Endpoint:**
```
POST /api/request-certificates
Host: localhost:9000
Content-Type: application/json
```

**Request Body:**
```json
{
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
  "address": "10.0.0.50",
  "network_instance": "EE"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Certificates generated successfully",
  "auth_certificate_id": "uuid-1",
  "sign_certificate_id": "uuid-2",
  "auth_certificate_pem": "-----BEGIN CERTIFICATE-----\n...",
  "sign_certificate_pem": "-----BEGIN CERTIFICATE-----\n..."
}
```

---

### 2️⃣ REGISTER SECURITY SERVER

**Endpoint:**
```
POST /api/security-servers/register
Host: localhost:9000
Content-Type: application/json
```

**Request Body:**
```json
{
  "registration_id": "REG_SS_001",
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "address": "10.0.0.50",
  "port": 9001,
  "network_instance": "EE",
  "auth_certificate_id": "uuid-1",
  "sign_certificate_id": "uuid-2",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
  "created_by": "admin@example.com"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Security server registered successfully",
  "registration": {
    "registration_id": "REG_SS_001",
    "server_id": "SECURITY_SERVER_1",
    "status": "registered",
    "registered_at": "2026-04-04T10:30:00Z"
  },
  "certificates": {
    "auth_certificate_id": "uuid-1",
    "sign_certificate_id": "uuid-2"
  },
  "crt_file": {
    "filename": "SECURITY_SERVER_1_registration.crt",
    "content": "[certificate content]"
  }
}
```

---

### 3️⃣ RETRIEVE REGISTRATION

**Endpoint:**
```
GET /api/security-servers/{server_id}
Host: localhost:9000
```

**Example:**
```
GET /api/security-servers/SECURITY_SERVER_1
```

**Response:**
```json
{
  "registration_id": "REG_SS_001",
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "address": "10.0.0.50",
  "port": 9001,
  "network_instance": "EE",
  "auth_certificate_id": "uuid-1",
  "sign_certificate_id": "uuid-2",
  "status": "registered",
  "created_at": "2026-04-04T10:30:00Z",
  "certificates": [
    {
      "certificate_id": "uuid-1",
      "certificate_type": "auth",
      "verified": true,
      "expiry_date": "2027-04-04T10:30:00Z"
    },
    {
      "certificate_id": "uuid-2",
      "certificate_type": "sign",
      "verified": true,
      "expiry_date": "2027-04-04T10:30:00Z"
    }
  ]
}
```

---

### 4️⃣ GET ALL REGISTRATIONS

**Endpoint:**
```
GET /api/security-servers/registrations
Host: localhost:9000
```

**Response:**
```json
[
  {
    "registration_id": "REG_SS_001",
    "server_id": "SECURITY_SERVER_1",
    "server_name": "Primary Gateway",
    "organization": "My Organization",
    "status": "registered",
    "created_at": "2026-04-04T10:30:00Z"
  },
  {
    "registration_id": "REG_SS_002",
    "server_id": "SECURITY_SERVER_2",
    "server_name": "Secondary Gateway",
    "organization": "My Organization",
    "status": "registered",
    "created_at": "2026-04-04T11:00:00Z"
  }
]
```

---

### 5️⃣ UPDATE REGISTRATION

**Endpoint:**
```
PUT /api/security-servers/{server_id}
Host: localhost:9000
Content-Type: application/json
```

**Request Body (all optional):**
```json
{
  "server_name": "Primary Gateway Updated",
  "address": "10.0.0.51",
  "port": 9002,
  "status": "active"
}
```

**Response:** Updated registration object

---

### 6️⃣ DELETE REGISTRATION

**Endpoint:**
```
DELETE /api/security-servers/{server_id}
Host: localhost:9000
```

**Response:**
```json
{
  "status": "success",
  "message": "Security server deregistered"
}
```

---

## Test Workflow with cURL

### Complete Registration Flow

```bash
#!/bin/bash

# 1. Generate Keys
openssl genrsa -out server.key 2048
openssl rsa -in server.key -pubout -out server.pub
PUBKEY=$(cat server.pub | tr '\n' '\\n')

# 2. Request Certificates
CERT_RESPONSE=$(curl -s -X POST http://localhost:9000/api/request-certificates \
  -H "Content-Type: application/json" \
  -d "{
    \"server_id\": \"SECURITY_SERVER_1\",
    \"server_name\": \"Primary Gateway\",
    \"organization\": \"My Organization\",
    \"public_key_pem\": \"$PUBKEY\",
    \"address\": \"10.0.0.50\",
    \"network_instance\": \"EE\"
  }")

AUTH_CERT_ID=$(echo $CERT_RESPONSE | jq -r '.auth_certificate_id')
SIGN_CERT_ID=$(echo $CERT_RESPONSE | jq -r '.sign_certificate_id')

echo "Certificates Generated!"
echo "AUTH Certificate ID: $AUTH_CERT_ID"
echo "SIGN Certificate ID: $SIGN_CERT_ID"

# 3. Register Server
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
    \"auth_certificate_id\": \"$AUTH_CERT_ID\",
    \"sign_certificate_id\": \"$SIGN_CERT_ID\",
    \"public_key_pem\": \"$PUBKEY\",
    \"created_by\": \"admin@example.com\"
  }")

echo $REGISTER_RESPONSE | jq .

# 4. Retrieve Registration
curl -s http://localhost:9000/api/security-servers/SECURITY_SERVER_1 | jq .
```

---

## Database Tables Created

```sql
-- Security Server Registrations
CREATE TABLE security_server_registrations (
    registration_id VARCHAR(100) PRIMARY KEY,
    server_id VARCHAR(100) UNIQUE,
    server_name VARCHAR(255),
    organization VARCHAR(255),
    address VARCHAR(100),
    port INT,
    network_instance VARCHAR(50),
    auth_certificate_id VARCHAR(100),
    sign_certificate_id VARCHAR(100),
    public_key_pem LONGTEXT,
    status VARCHAR(50),
    created_by VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Server Certificates
CREATE TABLE server_certificates (
    certificate_id VARCHAR(100) PRIMARY KEY,
    server_id VARCHAR(100),
    certificate_type VARCHAR(50),
    certificate_pem LONGTEXT,
    issued_date TIMESTAMP,
    expiry_date TIMESTAMP,
    thumbprint VARCHAR(512),
    verified BOOLEAN,
    created_at TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES security_server_registrations(server_id)
);
```

---

## Key Points

✅ **Two-Step Registration Process**:
1. Request certificates from CA
2. Register with verified certificates

✅ **Certificate Types**:
- **AUTH**: For TLS/HTTPS connections
- **SIGN**: For message signing/verification

✅ **Returned .crt File**:
- Contains registration confirmation
- Certificate IDs and metadata
- Can be stored locally for records

✅ **Database Tracking**:
- All registrations logged
- Certificate metadata stored
- Timestamps for audit trails

✅ **Error Handling**:
- Duplicate registration prevention
- CA service failure handling
- Comprehensive error messages

