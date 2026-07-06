# 🔐 Complete CSR → CRT Workflow - Step by Step

## Prerequisites Check

Before clicking "Get CRT", you MUST have completed these steps:

✅ **Step 0:** Network Configuration exists for gateway_code: `TEST_GW001`
✅ **Step 1:** Server Keys exist (key_id: 1 with public key data)
✅ **Step 2:** CSR is registered with matching key_id
⚠️ **Step 3:** Then click "Get CRT"

---

## Complete Working Workflow

### **PHASE 1: Create Gateway (Network Configuration)**

**URL:** System Configuration → Network Configuration

**Form:**
```
Title: Test Gateway
Version: 2.0
Network Instance: TEST
Gateway Code: TEST_GW001 ✓ (Must match CSR)
Entity ID: 1
Host: 192.168.1.100
Port: 9001
Hostname: test-gateway.local
IP Address: 192.168.1.100
Environment: Testing
```

Click **"Add Network Configuration"** button

---

### **PHASE 2: Create Server Keys**

**URL:** System Configuration → Network Configuration (same page, scroll down or use API)

**Create KEY 1 (AUTH):**

```json
POST /api/server-keys
{
  "gateway_code": "TEST_GW001",
  "key_type": "AUTH",
  "public_key": "-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ExKG
LklLbXKOMJAK7wqaGrQSdP7MjLjOpKJPzXpTx+TpjXxCQLpIuJ6rO7CZ9Q5vV8Qm
Wn7xU3ZqZ3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z
-----END PUBLIC KEY-----"
}
```

**Response will return:** `key_id: 1` ✓

---

### **PHASE 3: Register CSR with matching Key ID**

**URL:** Certificate Management → CSR Registration

**Click "Register New CSR":**

```
Gateway Code: TEST_GW001 ✓ (Must match network config)
Key ID: 1 ✓ (Must match server key you just created)
Type: AUTH
CSR Data: [Paste your CSR in PEM format]
```

Click **"Register CSR"** button

**Result:** CSR appears in table with status = PENDING

---

### **PHASE 4: Click "Get CRT" Button** ✓

Now that all dependencies exist:
- ✅ Network config: TEST_GW001 exists
- ✅ Server key: key_id = 1 exists  
- ✅ CSR: registered with gateway_code = TEST_GW001, key_id = 1

**Click "Get CRT"** in the Actions column

---

## API-Based Complete Workflow

If using cURL/Postman instead of frontend:

### **1. Create Network Config**
```bash
POST http://localhost:9000/api/network-config
{
  "title": "Test Gateway",
  "version": "2.0",
  "network_instance": "TEST",
  "gateway_code": "TEST_GW001",
  "entity_id": 1,
  "host": "192.168.1.100",
  "port": 9001,
  "hostname": "test-gateway.local",
  "ip_address": "192.168.1.100",
  "environment": "Testing"
}
```

### **2. Create Server Key (AUTH)**
```bash
POST http://localhost:9000/api/server-keys
{
  "gateway_code": "TEST_GW001",
  "key_type": "AUTH",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
}
```
✓ Returns: `key_id: 1`

### **3. Create Server Key (SIGN)**
```bash
POST http://localhost:9000/api/server-keys
{
  "gateway_code": "TEST_GW001",
  "key_type": "SIGN",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
}
```
✓ Returns: `key_id: 2`

### **4. Register CSR (AUTH)**
```bash
POST http://localhost:9000/api/certificate-requests
{
  "gateway_code": "TEST_GW001",
  "key_id": 1,
  "cert_type": "AUTH",
  "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"
}
```
✓ Returns: `csr_id: X`

### **5. Get CRT from CSR**
```bash
POST http://localhost:9000/api/certificate-requests/X/get-crt
```
✓ Returns: Certificate generated and stored!

---

## Your Current Issue

**Your CSR (ID: 2):**
```
Gateway Code: TEST_GW001
Key ID: 1
Type: AUTH
Status: PENDING
```

**Missing:**
```
❌ Server Key with key_id: 1 NOT FOUND
```

**Fix:**
1. Navigate to **System Configuration** → **Network Configuration**
2. Make sure gateway `TEST_GW001` is created
3. Then create server keys with the correct key_id
4. Return to CSR Registration
5. Click "Get CRT" ✓

---

## Debugging: Verify Prerequisites

### **Check Network Config Exists:**
```bash
curl http://localhost:9000/api/network-config/TEST_GW001
```

Expected: 200 OK with gateway details

### **Check Server Keys Exist:**
```bash
curl http://localhost:9000/api/server-keys/gateway/TEST_GW001
```

Expected: 200 OK with key list including key_id: 1

### **Check CSR Exists:**
```bash
curl http://localhost:9000/api/certificate-requests/2
```

Expected: 200 OK with CSR details

---

## Flow Diagram

```
┌─────────────────────────────────────┐
│ 1. Network Config (Gateway)         │
│    gateway_code = TEST_GW001        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. Server Keys (Public Keys)        │
│    key_id = 1 (AUTH)                │
│    key_id = 2 (SIGN)                │
│    gateway_code = TEST_GW001        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. CSR (Certificate Request)        │
│    csr_id = 2                       │
│    gateway_code = TEST_GW001        │
│    key_id = 1                       │
│    status = PENDING                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 4. Get CRT Button                   │
│    Sends CSR to CA Service          │
│    CA generates certificate         │
│    Certificate stored in DB         │
│    CSR status → SIGNED              │
└─────────────────────────────────────┘
```

---

## Frontend Screenshots

### Step 1: Network Configuration
```
Title: Test Gateway
Gateway Code: TEST_GW001
[Add Network Configuration] ✓
```

### Step 2: Server Keys (in same area, may need to scroll)
```
Add Server Key (AUTH)
  Gateway Code: TEST_GW001
  Key Type: AUTH
  Public Key: [paste public key]
[Add Key] ✓
→ Returns key_id: 1
```

### Step 3: Register CSR
```
Register New CSR
  Gateway Code: TEST_GW001
  Key ID: 1
  Type: AUTH
  CSR Data: [paste CSR]
[Register CSR] ✓
```

### Step 4: Get CRT
```
CSR Registration Table:
  CSR ID: 2
  Gateway Code: TEST_GW001
  Key ID: 1
  Type: AUTH
  Status: PENDING
  [Get CRT] ← Click here
```

---

## Service Prerequisites

✅ **Terminal 1:** CA Service running
```bash
python CA_management/ca_service.py
```

✅ **Terminal 2:** Global Server running
```bash
python gs1.py
```

✅ **Browser:** http://localhost:8000

---

## Common Errors & Fixes

### **Error: "Server key not found"**
❌ You clicked "Get CRT" before creating server key
✅ **Fix:** Create server key first (Step 2 above)

### **Error: "Network config not found"**
❌ Network configuration doesn't exist for gateway_code
✅ **Fix:** Create network configuration first (Step 1 above)

### **Error: "CSR not found"**
❌ CSR ID doesn't exist
✅ **Fix:** Register CSR first (Step 3 above)

### **Error: "Cannot connect to CA Service"**
❌ CA Service not running on port 9002
✅ **Fix:** Start CA Service: `python CA_management/ca_service.py`

---

## Next: Complete Success Flow

Once you complete all 4 steps:

1. ✅ Network Config: TEST_GW001 created
2. ✅ Server Keys: key_id 1 & 2 created  
3. ✅ CSR: Registered with key_id 1
4. ✅ Get CRT: Click button

**Result:**
- ✅ Certificate generated by CA Service
- ✅ Certificate stored in database
- ✅ CSR status updated to SIGNED
- ✅ New entry in Certificates table

**Certificate will show:**
- Cert ID: auto-generated
- Gateway Code: TEST_GW001
- Key ID: 1
- Type: AUTH
- Status: ACTIVE
- Valid From/To: dates from CA

---

## Test the Complete Flow

Use the test script:

```bash
python test_ca_integration.py
```

This will:
1. ✓ Check services running
2. ✓ Create CSR
3. ✓ Call Get CRT
4. ✓ Verify certificate stored
5. ✓ Show complete status

