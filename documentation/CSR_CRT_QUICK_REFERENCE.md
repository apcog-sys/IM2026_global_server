# CSR/CRT Registration - Quick Reference

## 3-Step Process

### Step 1️⃣ : Generate CSR (Security Server - Local)
```bash
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=SECURITY_SERVER_1"
```

### Step 2️⃣ : Submit CSR for CA Verification
```bash
POST /api/csr/verify

{
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "csr_file": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
  "address": "10.0.0.50",
  "network_instance": "EE"
}
```

**Response contains:**
- `certificate_id` - ID from CA
- `crt_file` - Signed certificate (PEM format)
- `thumbprint` - Certificate fingerprint
- `expiry_date` - When cert expires

### Step 3️⃣ : Register Server with Verified .crt
```bash
POST /api/security-servers/register

{
  "registration_id": "REG_SS_001",
  "server_id": "SECURITY_SERVER_1",
  "server_name": "Primary Gateway",
  "organization": "My Organization",
  "address": "10.0.0.50",
  "port": 9001,
  "network_instance": "EE",
  "csr_file": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
  "crt_file": "[from step 2 response]",
  "certificate_id": "[from step 2 response]",
  "thumbprint": "[from step 2 response]",
  "created_by": "admin@example.com"
}
```

**Response contains:**
- Registration confirmation
- `.crt` file to save locally
- `.metadata` file with registration details

## Minimal Python Example

```python
import requests
import subprocess

# Generate CSR
subprocess.run([
    'openssl', 'req', '-new', '-key', 'server.key', '-out', 'server.csr',
    '-subj', '/C=US/ST=State/L=City/O=Org/CN=SECURITY_SERVER_1'
])

with open('server.csr') as f:
    csr_content = f.read()

# Step 2: Verify CSR
r1 = requests.post('http://localhost:9000/api/csr/verify', json={
    'server_id': 'SECURITY_SERVER_1',
    'server_name': 'Primary Gateway',
    'organization': 'My Organization',
    'csr_file': csr_content,
    'address': '10.0.0.50',
    'network_instance': 'EE'
})

d1 = r1.json()
print(f"✓ CSR verified, cert_id: {d1['certificate_id']}")

# Step 3: Register
r2 = requests.post('http://localhost:9000/api/security-servers/register', json={
    'registration_id': 'REG_SS_001',
    'server_id': 'SECURITY_SERVER_1',
    'server_name': 'Primary Gateway',
    'organization': 'My Organization',
    'address': '10.0.0.50',
    'port': 9001,
    'network_instance': 'EE',
    'csr_file': csr_content,
    'crt_file': d1['crt_file'],
    'certificate_id': d1['certificate_id'],
    'thumbprint': d1['thumbprint'],
    'created_by': 'admin@example.com'
})

d2 = r2.json()
print(f"✓ Server registered: {d2['registration']['registration_id']}")

# Save files
with open(d2['crt_file']['filename'], 'w') as f:
    f.write(d2['crt_file']['content'])
print(f"✓ Saved: {d2['crt_file']['filename']}")
```

## Minimal cURL Example

```bash
# Generate CSR
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/C=US/ST=State/L=City/O=Org/CN=SECURITY_SERVER_1"

CSR=$(cat server.csr | tr '\n' '\\n')

# Step 2: Verify CSR
R1=$(curl -s -X POST http://localhost:9000/api/csr/verify \
  -H "Content-Type: application/json" \
  -d "{\"server_id\":\"SECURITY_SERVER_1\",\"server_name\":\"Primary Gateway\",\"organization\":\"My Organization\",\"csr_file\":\"$CSR\",\"address\":\"10.0.0.50\",\"network_instance\":\"EE\"}")

CRT=$(echo $R1 | jq -r '.crt_file')
CERT_ID=$(echo $R1 | jq -r '.certificate_id')
THUMB=$(echo $R1 | jq -r '.thumbprint')

# Step 3: Register
curl -s -X POST http://localhost:9000/api/security-servers/register \
  -H "Content-Type: application/json" \
  -d "{\"registration_id\":\"REG_SS_001\",\"server_id\":\"SECURITY_SERVER_1\",\"server_name\":\"Primary Gateway\",\"organization\":\"My Organization\",\"address\":\"10.0.0.50\",\"port\":9001,\"network_instance\":\"EE\",\"csr_file\":\"$CSR\",\"crt_file\":\"$CRT\",\"certificate_id\":\"$CERT_ID\",\"thumbprint\":\"$THUMB\",\"created_by\":\"admin@example.com\"}" | jq .
```

## What Gets Stored

| Item | Stored In | Format |
|------|-----------|--------|
| Original CSR | `csr_file` column | PEM text |
| Signed Cert | `crt_file` column | PEM text |
| Certificate ID | `certificate_id` column | UUID |
| Thumbprint | `thumbprint` column | SHA256 hash |
| Expiry | `expiry_date` column | Timestamp |

## File Names Returned

- **Certificate**: `{SERVER_ID}_registration.crt`
- **Metadata**: `{SERVER_ID}_registration.metadata`

Example:
- `SECURITY_SERVER_1_registration.crt`
- `SECURITY_SERVER_1_registration.metadata`

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `CSR verification failed` | Invalid CSR format | Regenerate CSR with valid config |
| `CA service error` | Port 9002 not accessible | Start CA service on port 9002 |
| `Server already registered` | `server_id` exists | Use different `server_id` |
| `Database not configured` | Haven't called `/api/init-db` | Configure database first |

## Management APIs

```bash
# List all registrations
curl http://localhost:9000/api/security-servers/registrations

# Get single server
curl http://localhost:9000/api/security-servers/SECURITY_SERVER_1

# Update server
curl -X PUT http://localhost:9000/api/security-servers/SECURITY_SERVER_1 \
  -H "Content-Type: application/json" \
  -d '{"port": 9002, "status": "active"}'

# Delete registration
curl -X DELETE http://localhost:9000/api/security-servers/SECURITY_SERVER_1
```

