# ⚡ Security Server Registration - Quick Reference

## 7-Step Flow at a Glance

```
┌─ STEP 1: Create Entity ─────────────────────┐
│ POST /api/entities                          │
│ Input: entity_code, entity_name             │
│ Output: entity_id = 1                       │
└─────────────────────────────────────────────┘
                    ↓
┌─ STEP 2: Register Gateway (PENDING) ────────┐
│ POST /api/network-config                    │
│ Input: gateway_code, entity_id, host, port  │
│ Auto: Logs "SUBMITTED"                      │
│ Status: PENDING                             │
└─────────────────────────────────────────────┘
                    ↓
┌─ STEP 3: Upload Keys ──────────────────────┐
│ POST /api/server-keys (AUTH)                │
│ POST /api/server-keys (SIGN)                │
│ Input: gateway_code, key_type, public_key   │
│ Output: key_id (1, 2)                       │
└─────────────────────────────────────────────┘
                    ↓
┌─ STEP 4: Submit CSRs (PENDING) ────────────┐
│ POST /api/certificate-requests (AUTH)       │
│ POST /api/certificate-requests (SIGN)       │
│ Input: gateway_code, key_id, csr_data       │
│ Status: PENDING                             │
└─────────────────────────────────────────────┘
                    ↓
┌─ STEP 5: Store Certificates (ACTIVE) ─────┐
│ POST /api/certificates (AUTH)               │
│ POST /api/certificates (SIGN)               │
│ Input: gateway_code, key_id, certificate    │
│ Auto: Updates CSR to "SIGNED"               │
│ Status: ACTIVE                              │
└─────────────────────────────────────────────┘
                    ↓
┌─ STEP 6: Admin Approval (APPROVED) ────────┐
│ POST /api/registration-log                  │
│ action: "APPROVED"                          │
│ Auto: Updates gateway status to APPROVED    │
│ Status: APPROVED                            │
└─────────────────────────────────────────────┘
                    ↓
┌─ STEP 7: Publish to Directory (ACTIVE) ────┐
│ POST /api/global-directory                  │
│ Input: entity_code, gateway_code, cert_ids  │
│ ⚠️  REQUIRES: gateway.status = APPROVED     │
│ Status: ACTIVE ✅ DISCOVERABLE              │
└─────────────────────────────────────────────┘
```

---

## One-Minute Summary

| Step | API Endpoint | Input | Key Output | Auto-Action |
|------|--------------|-------|-----------|-------------|
| 1️⃣ Create Entity | `POST /api/entities` | entity_code | entity_id: 1 | - |
| 2️⃣ Register Gateway | `POST /api/network-config` | gateway_code | gateway_code: GW001 | 📝 Logs SUBMITTED |
| 3️⃣ Upload Keys | `POST /api/server-keys` | key_type: AUTH/SIGN | key_id: 1,2 | - |
| 4️⃣ Submit CSRs | `POST /api/certificate-requests` | cert_type | csr_id: 1,2 | - |
| 5️⃣ Store Certs | `POST /api/certificates` | certificate | cert_id: 1,2 | 📝 Updates CSRs |
| 6️⃣ Approve | `POST /api/registration-log` | action: APPROVED | log_id | 📝 Status→APPROVED |
| 7️⃣ Publish | `POST /api/global-directory` | service_url | directory_id: 1 | ✅ DISCOVERABLE |

---

## Step-by-Step Commands

### STEP 1: Create Entity
```bash
curl -X POST http://localhost:9000/api/entities \
  -H "Content-Type: application/json" \
  -d '{"entity_code":"ORG1","entity_name":"My Organization","entity_type":"Organization","status":"ACTIVE"}'
```
➜ **Save**: entity_id = 1

---

### STEP 2: Register Gateway (PENDING)
```bash
curl -X POST http://localhost:9000/api/network-config \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "entity_id":1,
    "title":"Security Gateway",
    "version":"1.0",
    "network_instance":"PROD",
    "host":"192.168.1.100",
    "port":9001,
    "hostname":"gateway1.example.com",
    "ip_address":"192.168.1.100",
    "environment":"Production"
  }'
```
➜ **Gateway Status**: PENDING (auto-logged as SUBMITTED)

---

### STEP 3a: Upload AUTH Key
```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "key_type":"AUTH",
    "public_key":"-----BEGIN PUBLIC KEY-----\n[Your AUTH key]\n-----END PUBLIC KEY-----"
  }'
```
➜ **Save**: auth_key_id = 1

---

### STEP 3b: Upload SIGN Key
```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "key_type":"SIGN",
    "public_key":"-----BEGIN PUBLIC KEY-----\n[Your SIGN key]\n-----END PUBLIC KEY-----"
  }'
```
➜ **Save**: sign_key_id = 2

---

### STEP 4a: Submit AUTH CSR
```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "key_id":1,
    "cert_type":"AUTH",
    "csr_data":"-----BEGIN CERTIFICATE REQUEST-----\n[Your AUTH CSR]\n-----END CERTIFICATE REQUEST-----"
  }'
```
➜ **CSR Status**: PENDING

---

### STEP 4b: Submit SIGN CSR
```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "key_id":2,
    "cert_type":"SIGN",
    "csr_data":"-----BEGIN CERTIFICATE REQUEST-----\n[Your SIGN CSR]\n-----END CERTIFICATE REQUEST-----"
  }'
```
➜ **CSR Status**: PENDING

---

### STEP 5a: Store AUTH Certificate
```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "key_id":1,
    "cert_type":"AUTH",
    "certificate":"-----BEGIN CERTIFICATE-----\n[CA-signed AUTH cert]\n-----END CERTIFICATE-----",
    "issued_by":"GlobalCA",
    "valid_from":"2026-04-11T10:00:00",
    "valid_to":"2027-04-11T10:00:00"
  }'
```
➜ **Cert Status**: ACTIVE, **CSR auto-updated to**: SIGNED  
➜ **Save**: auth_cert_id = 1

---

### STEP 5b: Store SIGN Certificate
```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "key_id":2,
    "cert_type":"SIGN",
    "certificate":"-----BEGIN CERTIFICATE-----\n[CA-signed SIGN cert]\n-----END CERTIFICATE-----",
    "issued_by":"GlobalCA",
    "valid_from":"2026-04-11T10:01:00",
    "valid_to":"2027-04-11T10:01:00"
  }'
```
➜ **Cert Status**: ACTIVE, **CSR auto-updated to**: SIGNED  
➜ **Save**: sign_cert_id = 2

---

### STEP 6: Admin Approval
```bash
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code":"GW001",
    "action":"APPROVED",
    "performed_by":"admin@example.com",
    "remarks":"Gateway verified and approved"
  }'
```
➜ **Gateway Status**: AUTO-UPDATED to APPROVED  
➜ **Ready for**: Publishing to directory

---

### STEP 7: Publish to Global Directory
```bash
curl -X POST http://localhost:9000/api/global-directory \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code":"ORG1",
    "gateway_code":"GW001",
    "service_url":"https://gateway1.example.com:9001",
    "auth_cert_id":1,
    "sign_cert_id":2
  }'
```
➜ **Status**: ACTIVE  
✅ **NOW DISCOVERABLE by other systems**

---

## Verify Each Step

```bash
# Check gateway status
curl http://localhost:9000/api/network-config/GW001

# Check audit trail
curl http://localhost:9000/api/registration-log/gateway/GW001

# Check pending CSRs
curl "http://localhost:9000/api/certificate-requests?status=PENDING"

# Check signed certificates
curl http://localhost:9000/api/certificates/gateway/GW001

# Discover server
curl http://localhost:9000/api/global-directory
```

---

## Status Values

| Table | Field | Values |
|-------|-------|--------|
| network_config | status | PENDING → APPROVED → REJECTED |
| certificate_requests | status | PENDING → SIGNED → REJECTED |
| certificates | status | ACTIVE → EXPIRED/REVOKED |
| global_directory | status | ACTIVE → INACTIVE |
| registration_log | action | SUBMITTED, APPROVED, REJECTED |

---

## Key Rules

✅ **STEP 6 (Approval) must complete before STEP 7 (Publishing)**
- Attempting to publish without APPROVED status → Error 400

✅ **STEP 5 auto-actions**:
- Storing certificate → CSR auto-updated to SIGNED
- Logging approval → network_config auto-updated to APPROVED

✅ **Complete transaction example**:
1. Register gateway (PENDING)
2. Upload 2 keys
3. Submit 2 CSRs
4. Store 2 certs (CSRs update to SIGNED automatically)
5. Approve gateway (status updates to APPROVED automatically)
6. Publish to directory (now ACTIVE and DISCOVERABLE)

---

## Error Codes

| Code | Reason | Solution |
|------|--------|----------|
| 400 | Gateway not APPROVED | Complete Step 6 first |
| 404 | Resource not found | Verify gateway_code, entity_id, key_id |
| 409 | Duplicate gateway_code | Each security server must have unique code |
| 500 | Database error | Check database configuration |

---

## What Happens Automatically

| Action | Auto-Triggered | Result |
|--------|-----------------|--------|
| `POST /api/network-config` | Creates log entry | registration_log.action = SUBMITTED |
| `POST /api/certificates` | Updates CSR | certificate_requests.status = SIGNED |
| `POST /api/registration-log` (APPROVED) | Updates gateway | network_config.status = APPROVED |
| `POST /api/registration-log` (REJECTED) | Updates gateway | network_config.status = REJECTED |

