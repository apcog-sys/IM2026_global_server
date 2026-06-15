# CA Management Refactoring - Migration Guide

## Overview

The Certificate Authority (CA) system has been **completely refactored** and moved to a separate, independent micro-service called `CA_management` running on **port 9002**.

## What Changed

### ✅ New Architecture

**Before** (Monolithic):
- All PKI code in main security server
- Endpoints mixed with gateway logic
- Tight coupling between services
- All on port 9001

**After** (Microservices):
- Dedicated CA_management micro-service
- Isolated endpoints on port 9002  
- Cleanly separated concerns
- Independent deployment and scaling

### 📁 File Structure

```
CA_management/                    # ✨ NEW - Separate CA system
├── ca_authority.py             # Root CA implementation
├── certificate_manager.py       # Certificate management layer
├── ca_service.py                # FastAPI service (port 9002)
├── README.md                    # Complete documentation  
├── __init__.py                  # Package initialization
├── pki/                         # Auto-generated (Certificate storage)
│   ├── keys/
│   │   └── ca_private_key.pem
│   └── certs/
│       ├── ca_root.crt
│       ├── auth_*.crt
│       └── sign_*.crt
└── tests/
    ├── test_ca_system.py        # Test suite
    └── __init__.py
```

### 🎯 Key Changes to Terminology

All "X-Road" and "XROAD" terminology has been replaced with generic, framework-agnostic names:

| Old Name | New Name | Reason |
|----------|----------|--------|
| `xroad_certificate_manager.py` | `certificate_manager.py` | Generic naming |
| `XRoadCertificateManager` | `CertificateManager` | Framework-agnostic |
| `get_pki_ca()` | `get_certificate_authority()` | Descriptive |
| `pki_ca_manager.py` | `ca_authority.py` | Clarified purpose |
| `PKICertificateAuthority` | `CertificateAuthority` | Simplified |
| X-Road Root CA | Root Certification Authority | Generic |
| X-Road OIDs | Standard X.509 extensions | Industry standard |

### 🚀 Running the CA Service

#### Option 1: Direct Python
```bash
cd /path/to/Security_server1
python CA_management/ca_service.py
```

#### Option 2: Using Uvicorn
```bash
cd /path/to/Security_server1
uvicorn CA_management.ca_service:app --port 9002
```

#### Option 3: Background Process
```bash
cd /path/to/Security_server1
nohup python CA_management/ca_service.py > ca_service.log 2>&1 &
```

### 📡 Updated Endpoints

**Main Security Server (Port 9001)**:
- All certificate operations REMOVED
- See CA_management service instead

**CA Management Service (Port 9002)** - NEW:
- `POST   /api/certificates/generate-auth`
- `POST   /api/certificates/generate-sign`  
- `POST   /api/certificates/generate-both`
- `GET    /api/certificates/ca-root`
- `GET    /api/certificates/{server_id}/chain`
- `GET    /api/certificates/server/{server_id}`
- `GET    /api/certificates/{cert_id}`
- `GET    /health`

### 🧪 Testing

```bash
cd /path/to/Security_server1

# 1. Start CA service (first terminal)
python CA_management/ca_service.py

# 2. Run tests (second terminal)
python CA_management/tests/test_ca_system.py
```

Expected output:
```
✅ PASS - Health Check
✅ PASS - Generate Authentication Certificate
✅ PASS - Generate Signature Certificate
✅ PASS - Generate Both Certificates
✅ PASS - Get CA Root Certificate
✅ PASS - Get Certificate Chain
✅ PASS - Get Server Certificates

🎉 All tests passed successfully!
```

## API Examples

### Python (requests)
```python
import requests

# Generate both certificates
response = requests.post(
    "http://localhost:9002/api/certificates/generate-both",
    json={
        "server_id": "SECURITY_SERVER_1",
        "server_name": "Gateway",
        "organization": "My Org",
        "address": "10.0.0.50",
        "public_key_pem": open("keys/auth_public.pem").read()
    }
)

certs = response.json()
print(f"AUTH: {certs['auth_certificate']['thumbprint']}")
print(f"SIGN: {certs['sign_certificate']['thumbprint']}")
```

### cURL
```bash
curl -X POST http://localhost:9002/api/certificates/generate-auth \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "SECURITY_SERVER_1",
    "server_name": "Gateway",
    "organization": "My Org",
    "address": "10.0.0.50",
    "public_key_pem": "'"$(cat keys/auth_public.pem)"'"
  }'
```

### PowerShell
```powershell
$body = @{
    server_id = "SECURITY_SERVER_1"
    server_name = "Gateway"
    organization = "My Org"
    address = "10.0.0.50" 
    public_key_pem = Get-Content keys/auth_public.pem -Raw
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:9002/api/certificates/generate-auth" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

## Database Integration

Certificates are still stored in **MySQL** database:

**Table**: `security_server_certificates`

**Columns**:
- `certificate_id` - UUID
- `server_id` - Server identifier
- `certificate_type` - "auth" or "sign"
- `thumbprint` - SHA-256 fingerprint
- `certificate_path` - Filesystem location
- `issued_date` - Generation timestamp
- `expiry_date` - Expiration timestamp
- `status` - ACTIVE/EXPIRED/REVOKED
- `created_at` - Record creation time

**Query Example**:
```sql
-- Get all active certificates for a server
SELECT certificate_id, certificate_type, thumbprint, expiry_date
FROM security_server_certificates
WHERE server_id = 'SECURITY_SERVER_1' AND status = 'ACTIVE';
```

## Security Features

### Cryptography
- **Algorithm**: RSA-4096 bits
- **Hashing**: SHA-256
- **Format**: X.509 v3
- **Validity**: 365 days (certificates), 10 years (root CA)

### Key Storage
- Root CA private key: `CA_management/pki/keys/ca_private_key.pem`
- Recommended file permissions: `chmod 600` (owner read/write only)
- **NEVER** share or expose this file

### Network
- CA service runs on localhost:9002 by default
- Firewall: Restrict access to authorized servers only
- Consider HTTPS/TLS for production deployment

## Migration Checklist

- [ ] Review CA_management/README.md
- [ ] Start CA service: `python CA_management/ca_service.py`
- [ ] Run test suite: `python CA_management/tests/test_ca_system.py`
- [ ] Verify all tests pass
- [ ] Update internal API calls to use `http://localhost:9002`
- [ ] Test certificate generation workflow
- [ ] Verify MySQL storage of certificates
- [ ] Check file permissions on `CA_management/pki/keys/`
- [ ] Set up process monitoring/auto-restart
- [ ] Update deployment documentation
- [ ] Train operations team on new structure

## Troubleshooting

### "Connection refused on port 9002"
- Verify CA service is running
- Check firewall settings
- Ensure port 9002 is available

### "Database connection failed"
- Verify MySQL is running
- Check database credentials in `ca_service.py`
- Ensure `service_gateway` database exists

### "Root CA not found"
- Delete `CA_management/pki/` directory
- Restart CA service (will regenerate root CA)
- Root CA is persistent and auto-creates on first run

### "Certificate generation slow"
- This is expected (RSA-4096 takes 5-10 seconds)
- Verify no other heavy processes running
- Check disk I/O performance

## Performance Characteristics

- **Certificate Generation**: 5-10 seconds (RSA-4096 cryptography)
- **API Response Time**: Same as generation time
- **Database Queries**: < 100ms
- **Memory Usage**: ~50MB baseline
- **Startup Time**: < 5 seconds
- **Throughput**: Sequential (not parallel yet)

## Next Steps

1. ✅ Read: [CA_management/README.md](CA_management/README.md)
2. ✅ Start: `python CA_management/ca_service.py`
3. ✅ Test: `python CA_management/tests/test_ca_system.py`  
4. ✅ Deploy: Configure firewall and process monitoring
5. ✅ Integrate: Update internal clients to use port 9002

## File Organization

**Original Location** → **New Location**:
- `pki_ca_manager.py` → `CA_management/ca_authority.py` (refactored)
- `xroad_certificate_manager.py` → `CA_management/certificate_manager.py` (refactored)
- `test_xroad_pki.py` → `CA_management/tests/test_ca_system.py` (refactored)
- `XROAD_PKI_GUIDE.md` → Obsolete (see CA_management/README.md)
- `XROAD_PKI_QUICKREF.md` → Obsolete (see CA_management/README.md)
- `XROAD_PKI_IMPLEMENTATION.md` → Obsolete (see CA_management/README.md)

## Benefits of Refactoring

✅ **Isolation**: CA runs independently - failures don't affect main server  
✅ **Scalability**: Can run multiple CA instances  
✅ **Maintainability**: Clean separation of concerns  
✅ **Testability**: Dedicated test suite for CA  
✅ **Debugging**: Easier to trace CA-specific issues  
✅ **Reusability**: Can be integrated into other services  
✅ **Generic**: Framework-agnostic naming (works with any framework)  
✅ **Modern**: Micro-services architecture  

## Support

For detailed information, see:
- [CA_management/README.md](CA_management/README.md) - Complete documentation
- [CA_management/tests/test_ca_system.py](CA_management/tests/test_ca_system.py) - Usage examples
- [CA_management/ca_authority.py](CA_management/ca_authority.py) - Implementation details
- [CA_management/certificate_manager.py](CA_management/certificate_manager.py) - API layer

---

**Status**: ✅ **Refactoring Complete**  
**Date**: 2026-03-31  
**Version**: 1.0.0
