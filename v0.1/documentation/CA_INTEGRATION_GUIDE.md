# 🔐 CA Integration Guide - CSR to CRT Workflow

## Overview

The system now has a **complete CSR → CRT workflow**:
1. CSR is registered via frontend or API
2. Click "Get CRT" button to send CSR to CA Authority
3. CA generates signed certificate
4. CRT is automatically stored in certificates table
5. CSR status automatically updated to SIGNED

---

## Architecture

```
┌──────────────────────────────────────┐
│  Frontend (Port 8000)                │
│  - Register CSR                      │
│  - Click "Get CRT" button            │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  Global Server (Port 9000)           │ ← gs1.py
│  - New endpoint: /api/certificate-  │
│    requests/{csr_id}/get-crt         │
│  - Calls CA Service                  │
│  - Stores CRT in database            │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  CA Management Service (Port 9002)   │ ← ca_service.py
│  - Generate AUTH certificate         │
│  - Generate SIGN certificate         │
│  - Return signed CRT                 │
└──────────────────────────────────────┘
```

---

## Starting the Services

### **1. Start CA Service (FIRST - in Terminal 1)**

```bash
cd c:\Users\Sahique\Desktop\new_workspace\2026\Information_mediator_v2\global_server

python CA_management/ca_service.py
```

**Expected Output:**
```
[CA-AUTH] Certificate Authority initialized
INFO:     Uvicorn running on http://0.0.0.0:9002
[CA-SERVICE] Certificate Manager initialized successfully
```

### **2. Start Global Server (in Terminal 2)**

```bash
python gs1.py
```

**Expected Output:**
```
✓ Server started. Connected to database.
INFO:     Uvicorn running on http://0.0.0.0:9000
```

### **3. Access Frontend (in Browser)**

```
http://localhost:8000
```

---

## How It Works

### **Step 1: Register CSR (Frontend)**

1. Navigate to **Certificate Management** → **CSR Registration**
2. Click **"Register New CSR"** button
3. Fill in:
   - Gateway Code: `TEST_GW001`
   - Key ID: `1`
   - Type: `AUTH` or `SIGN`
   - CSR Data (PEM format)
4. Click **Register CSR**
5. CSR appears in table with status: **PENDING**

### **Step 2: Generate Certificate (Frontend)**

1. Find your CSR in the table (with PENDING status)
2. Click **"Get CRT"** button (green button)
3. Confirm the dialog: "Send CSR to CA Management to generate Certificate?"
4. System shows: "Processing..."
5. Backend workflow:
   - Retrieves CSR details (gateway_code, key_id, cert_type)
   - Gets public key from server_keys table
   - Calls CA Service: `/api/certificates/generate-auth` or `generate-sign`
   - CA Service returns signed certificate
   - Certificate stored in certificates table
   - CSR status updated to **SIGNED**
6. Success message: "Certificate generated successfully! (Cert ID: 1)"

### **Step 3: View Certificate (Frontend)**

1. Navigate to **Certificate Management** → **Certificates**
2. New certificate appears in table:
   - Cert ID
   - Gateway Code
   - Type (AUTH/SIGN badge)
   - Status: **ACTIVE**
   - Valid From/To dates

---

## Backend Endpoint

### **POST `/api/certificate-requests/{csr_id}/get-crt`**

**What it does:**
- Converts CSR to signed CRT certificate
- Calls CA Service on port 9002
- Stores certificate in database
- Updates CSR status to SIGNED

**Request:**
```bash
curl -X POST http://localhost:9000/api/certificate-requests/2/get-crt
```

**Response:**
```json
{
  "status": "success",
  "message": "Certificate generated and stored successfully",
  "cert_id": 1,
  "csr_id": 2,
  "gateway_code": "TEST_GW001",
  "cert_type": "AUTH",
  "certificate": "-----BEGIN CERTIFICATE-----\n..."
}
```

**Error Responses:**
- **503 - CA Service Connection Error**
  ```json
  {
    "detail": "Cannot connect to CA Service. Is it running on port 9002? 
    Start it with: python CA_management/ca_service.py"
  }
  ```

- **404 - CSR Not Found**
  ```json
  {
    "detail": "CSR not found"
  }
  ```

---

## Database Changes

### **CSR Registration Workflow**

| Field | Before | After |
|-------|--------|-------|
| status | PENDING | SIGNED |
| requested_at | Auto-set | Unchanged |

### **New Certificate Stored**

```sql
INSERT INTO certificates 
(gateway_code, key_id, cert_type, certificate, issued_by, valid_from, valid_to, status)
VALUES 
('TEST_GW001', 1, 'AUTH', '-----BEGIN CERTIFICATE-----...', 'CA Authority', '2026-04-14...', '2027-04-14...', 'ACTIVE')
```

---

## Complete Workflow Example

### **Terminal 1: Start CA Service**
```bash
$ python CA_management/ca_service.py
[CA-AUTH] Certificate Authority initialized
INFO:     Uvicorn running on http://0.0.0.0:9002
```

### **Terminal 2: Start Global Server**
```bash
$ python gs1.py
✓ Server started. Connected to database.
INFO:     Uvicorn running on http://0.0.0.0:9000
```

### **Browser: Frontend Operations**

1. Go to http://localhost:8000
2. Navigate to **Certificate Management** → **CSR Registration**
3. Click **Register New CSR**
4. Fill form:
   - Gateway Code: `GW_PROD_001`
   - Key ID: `5`
   - Type: `SIGN`
   - CSR Data: [paste CSR in PEM format]
5. Click **Register CSR**
6. Table shows new CSR with PENDING status
7. Click **Get CRT** button (green)
8. Watch the processing...
9. Success! ✓ Certificate generated successfully!
10. CSR status now shows: **SIGNED**
11. Navigate to **Certificates** tab
12. See new certificate with status: **ACTIVE**

---

## API Flow Diagram

```
Frontend (8000)
    │
    ├─► POST /api/certificate-requests
    │   └─► Stores CSR in database
    │
    └─► POST /api/certificate-requests/{csr_id}/get-crt
        │
        ├─► Get CSR from database
        ├─► Get server_key (public key)
        ├─► Get network_config (server info)
        │
        └─► Call CA Service (9002)
            │
            ├─► POST /api/certificates/generate-auth (or generate-sign)
            │
            └─► Return CRT
                │
                ├─► Store in certificates table
                ├─► Update CSR status to SIGNED
                │
                └─► Return success to frontend
```

---

## Troubleshooting

### **Error: "Cannot connect to CA Service"**
- ✅ Make sure CA Service is running: `python CA_management/ca_service.py`
- ✅ Check port 9002 is available
- ✅ Check firewall isn't blocking port 9002

### **Error: "Server key not found"**
- ✅ Create server key first: **Network Configuration** → Add Key
- ✅ Key ID in CSR must match server_keys table

### **Error: "Network config not found"**
- ✅ Create network config first: **System Configuration** → Network Configuration
- ✅ Gateway code must exist in network_config table

### **Certificate not appearing in Certificates tab**
- ✅ Refresh browser (F5)
- ✅ Check browser console for errors (F12)
- ✅ Verify certificate was inserted in database

---

## Files Modified/Created

| Component | File | Changes |
|-----------|------|---------|
| **Backend** | gs1.py | Added `import requests` + New endpoint `/api/certificate-requests/{csr_id}/get-crt` |
| **Frontend** | index.html | Added "Get CRT" button + `getCrtFromCsr()` function |
| **CA Service** | CA_management/ca_service.py | (No changes - already operational) |

---

## Testing the Integration

### **Test 1: Verify Services Running**
```bash
# Terminal 1
curl http://localhost:9002/health

# Response: {"status": "healthy", "service": "Certificate Authority", ...}

# Terminal 2 (different)
curl http://localhost:9000/health

# Response: {"status": "healthy", "db_configured": true, ...}
```

### **Test 2: Register CSR via API**
```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "TEST_GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"
  }'
```

### **Test 3: Get CRT via API**
```bash
curl -X POST http://localhost:9000/api/certificate-requests/1/get-crt
```

### **Test 4: Verify Certificate in Database**
```bash
# In MySQL
SELECT * FROM certificates WHERE csr_id = 1;
```

---

## Security Notes

- ✅ CSR status auto-updates to SIGNED (prevents double processing)
- ✅ Certificate stored with ACTIVE status ready to use
- ✅ CA Service isolated on separate port (9002)
- ✅ All certificate data encrypted in transit (use HTTPS in production)
- ✅ Database credentials in config.json

---

## Next Steps

After getting CRTs:

1. **Register to Global Server**
   - Navigate to **Global Server Configuration**
   - Paste both AUTH and SIGN certificates
   - Submit for global discovery

2. **Monitor Certificate Status**
   - Check expiry dates regularly
   - Renew certificates before expiration
   - Track certificate usage via registration log

3. **Audit & Compliance**
   - Use **Registration Log** to track all approvals
   - Export certificate chains for compliance
   - Monitor certificate validity periods

---

## Contact & Support

For issues or questions:
- Check **Console** tab in browser (F12) for frontend errors
- Check terminal output for backend errors
- Verify all services running on correct ports
- Check database connectivity: **System Configuration** → **Test Connection**
