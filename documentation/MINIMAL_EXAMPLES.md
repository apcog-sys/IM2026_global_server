# Minimal Request Body Examples

## Step 1: Request Certificates (Minimum Fields)

```json
{
  "server_id": "SS_1",
  "server_name": "Gateway A",
  "organization": "ORG_NAME",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...[key content]...\n-----END PUBLIC KEY-----",
  "address": "10.0.0.50",
  "network_instance": "EE"
}
```

**Returns:**
```json
{
  "status": "success",
  "auth_certificate_id": "cert-id-1",
  "sign_certificate_id": "cert-id-2",
  "auth_certificate_pem": "-----BEGIN CERTIFICATE-----\n...",
  "sign_certificate_pem": "-----BEGIN CERTIFICATE-----\n..."
}
```

---

## Step 2: Register Server (Use Values from Step 1)

```json
{
  "registration_id": "REG_SS_1",
  "server_id": "SS_1",
  "server_name": "Gateway A",
  "organization": "ORG_NAME",
  "address": "10.0.0.50",
  "port": 9001,
  "network_instance": "EE",
  "auth_certificate_id": "cert-id-1",
  "sign_certificate_id": "cert-id-2",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...[key content]...\n-----END PUBLIC KEY-----",
  "created_by": "admin@org.com"
}
```

**Returns:**
```json
{
  "status": "success",
  "crt_file": {
    "filename": "SS_1_registration.crt",
    "content": "[certificate content]"
  }
}
```

---

## Using Python Requests

```python
import requests
import json

# Step 1: Request Certificates
cert_response = requests.post(
    'http://localhost:9000/api/request-certificates',
    json={
        'server_id': 'SS_1',
        'server_name': 'Gateway A',
        'organization': 'ORG_NAME',
        'public_key_pem': open('server.pub').read(),
        'address': '10.0.0.50',
        'network_instance': 'EE'
    }
)

cert_data = cert_response.json()
auth_id = cert_data['auth_certificate_id']
sign_id = cert_data['sign_certificate_id']

# Step 2: Register Server
register_response = requests.post(
    'http://localhost:9000/api/security-servers/register',
    json={
        'registration_id': 'REG_SS_1',
        'server_id': 'SS_1',
        'server_name': 'Gateway A',
        'organization': 'ORG_NAME',
        'address': '10.0.0.50',
        'port': 9001,
        'network_instance': 'EE',
        'auth_certificate_id': auth_id,
        'sign_certificate_id': sign_id,
        'public_key_pem': open('server.pub').read(),
        'created_by': 'admin@org.com'
    }
)

print(register_response.json())
```

---

## Using PowerShell

```powershell
# Step 1: Request Certificates
$certRequest = @{
    server_id = 'SS_1'
    server_name = 'Gateway A'
    organization = 'ORG_NAME'
    public_key_pem = Get-Content 'server.pub' -Raw
    address = '10.0.0.50'
    network_instance = 'EE'
} | ConvertTo-Json

$certResponse = Invoke-RestMethod -Uri 'http://localhost:9000/api/request-certificates' `
    -Method Post -ContentType 'application/json' -Body $certRequest

$authId = $certResponse.auth_certificate_id
$signId = $certResponse.sign_certificate_id

# Step 2: Register Server
$registerRequest = @{
    registration_id = 'REG_SS_1'
    server_id = 'SS_1'
    server_name = 'Gateway A'
    organization = 'ORG_NAME'
    address = '10.0.0.50'
    port = 9001
    network_instance = 'EE'
    auth_certificate_id = $authId
    sign_certificate_id = $signId
    public_key_pem = Get-Content 'server.pub' -Raw
    created_by = 'admin@org.com'
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Uri 'http://localhost:9000/api/security-servers/register' `
    -Method Post -ContentType 'application/json' -Body $registerRequest

$registerResponse | ConvertTo-Json
```

---

## Checking Registration Status

### Get All

```bash
curl http://localhost:9000/api/security-servers/registrations
```

### Get Single Server

```bash
curl http://localhost:9000/api/security-servers/SS_1
```

### Update Server

```bash
curl -X PUT http://localhost:9000/api/security-servers/SS_1 \
  -H "Content-Type: application/json" \
  -d '{"port": 9002, "status": "active"}'
```

### Delete Registration

```bash
curl -X DELETE http://localhost:9000/api/security-servers/SS_1
```

---

## Field Descriptions

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `server_id` | String | ✅ | `SS_1` |
| `server_name` | String | ✅ | `Gateway A` |
| `organization` | String | ✅ | `ORG_NAME` |
| `public_key_pem` | String | ✅ | `-----BEGIN PUBLIC KEY-----...` |
| `address` | String | ✅ | `10.0.0.50` |
| `network_instance` | String | ✅ | `EE` |
| `registration_id` | String | ✅ | `REG_SS_1` |
| `port` | Integer | ✅ | `9001` |
| `created_by` | String | ✅ | `admin@org.com` |
| `auth_certificate_id` | String | ✅ (from Step 1) | UUID |
| `sign_certificate_id` | String | ✅ (from Step 1) | UUID |

---

## Error Responses

### Server Already Registered
```json
{
  "status": "error",
  "message": "Security server with ID 'SS_1' is already registered"
}
```
**Status Code:** 409 Conflict

### CA Service Down
```json
{
  "status": "error",
  "message": "Failed to connect to Certificate Authority service"
}
```
**Status Code:** 502 Bad Gateway

### Missing Field
```json
{
  "status": "error",
  "message": "Missing required field: server_name"
}
```
**Status Code:** 400 Bad Request

