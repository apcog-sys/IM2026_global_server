# 📖 Security Server Registration - Documentation Index

## Quick Links

### 🚀 Just Want to Get Started?
→ Start here: [QUICK_REFERENCE_FLOW.md](QUICK_REFERENCE_FLOW.md) - One page overview

### 🧪 Ready to Test?
→ Go here: [TEST_COMMANDS.md](TEST_COMMANDS.md) - Copy & paste commands

### 📚 Need Complete Details?
→ Read this: [SECURITY_SERVER_REGISTRATION_FLOW.md](SECURITY_SERVER_REGISTRATION_FLOW.md) - Full explanation

---

## What Each Document Contains

| Document | Purpose | Audience | Length |
|----------|---------|----------|--------|
| **QUICK_REFERENCE_FLOW.md** | 7-step flow at a glance + key commands | Everyone | 1 page |
| **TEST_COMMANDS.md** | Ready-to-copy curl commands + test script | Testers | 2 pages |
| **SECURITY_SERVER_REGISTRATION_FLOW.md** | Complete step-by-step guide | Engineers | 5 pages |
| **FULL_CRUD_API_REFERENCE.md** | All CRUD operations for all 7 tables | Developers | 10+ pages |
| **ENDPOINT_REFERENCE.md** | All 41 HTTP endpoints | API Users | 5+ pages |

---

## 7-Step Registration Overview

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: CREATE ENTITY                                      │
│  POST /api/entities → entity_id                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: REGISTER GATEWAY (PENDING)                         │
│  POST /api/network-config → Status: PENDING                 │
│  Auto-logs: SUBMITTED                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: UPLOAD PUBLIC KEYS                                 │
│  POST /api/server-keys (AUTH)                               │
│  POST /api/server-keys (SIGN)                               │
│  → key_id values                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: SUBMIT CSRs (PENDING)                              │
│  POST /api/certificate-requests (AUTH)                      │
│  POST /api/certificate-requests (SIGN)                      │
│  → Status: PENDING                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: STORE CERTIFICATES (ACTIVE)                        │
│  POST /api/certificates (AUTH)                              │
│  POST /api/certificates (SIGN)                              │
│  Auto-updates CSR → SIGNED                                  │
│  → Status: ACTIVE                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: ADMIN APPROVAL (APPROVED)                          │
│  POST /api/registration-log (action: APPROVED)              │
│  Auto-updates gateway → APPROVED                            │
│  ⚠️ Required before Step 7!                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: PUBLISH TO DIRECTORY (ACTIVE)                      │
│  POST /api/global-directory                                 │
│  ✅ NOW DISCOVERABLE BY OTHER SYSTEMS                       │
│  → Status: ACTIVE                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Endpoints by Step

| Step | Endpoint | Method | Purpose |
|------|----------|--------|---------|
| 1 | `/api/entities` | POST | Create organization |
| 2 | `/api/network-config` | POST | Register gateway (PENDING) |
| 3 | `/api/server-keys` | POST | Upload AUTH key |
| 3 | `/api/server-keys` | POST | Upload SIGN key |
| 4 | `/api/certificate-requests` | POST | Submit AUTH CSR (PENDING) |
| 4 | `/api/certificate-requests` | POST | Submit SIGN CSR (PENDING) |
| 5 | `/api/certificates` | POST | Store AUTH certificate (ACTIVE) |
| 5 | `/api/certificates` | POST | Store SIGN certificate (ACTIVE) |
| 6 | `/api/registration-log` | POST | Log approval (updates to APPROVED) |
| 7 | `/api/global-directory` | POST | Publish to directory (ACTIVE) |

---

## Status Progression

```
Step 1: entity.status = ACTIVE
             ↓
Step 2: network_config.status = PENDING
             ↓
Step 3: (Keys uploaded - no status change)
             ↓
Step 4: certificate_requests.status = PENDING
             ↓
Step 5: certificates.status = ACTIVE
        certificate_requests.status = SIGNED ← AUTO
             ↓
Step 6: network_config.status = APPROVED ← AUTO
             ↓
Step 7: global_directory.status = ACTIVE
        ✅ DISCOVERABLE
```

---

## Auto-Actions

| Action | Triggered By | Auto Result |
|--------|--------------|------------|
| Log SUBMITTED | `POST /api/network-config` | registration_log entry created |
| Update CSR to SIGNED | `POST /api/certificates` | certificate_requests.status = SIGNED |
| Update gateway to APPROVED | `POST /api/registration-log` (APPROVED) | network_config.status = APPROVED |
| Update gateway to REJECTED | `POST /api/registration-log` (REJECTED) | network_config.status = REJECTED |

---

## Sample Data to Use for Testing

```json
{
  "entity_code": "TEST_ORG",
  "entity_name": "Test Organization",
  "entity_type": "Organization",
  "gateway_code": "TEST_GW001",
  "hostname": "test-gateway.local",
  "host": "192.168.1.100",
  "port": 9001,
  "service_url": "https://test-gateway.local:9001",
  "admin_email": "admin@test.com"
}
```

---

## Verification Commands After Complete Flow

```bash
# Check gateway status (should be APPROVED)
curl http://localhost:9000/api/network-config/TEST_GW001

# Check audit trail (should show SUBMITTED, APPROVED)
curl http://localhost:9000/api/registration-log/gateway/TEST_GW001

# Check CSRs (should show SIGNED)
curl "http://localhost:9000/api/certificate-requests?status=SIGNED"

# Check certificates (should show ACTIVE)
curl http://localhost:9000/api/certificates/gateway/TEST_GW001

# Discover gateway (should appear in directory)
curl http://localhost:9000/api/global-directory
```

---

## Requirements Before Starting

✅ **Server Running**
```bash
python gs1.py
```

✅ **Database Configured**
```bash
curl -X POST http://localhost:9000/api/save-db-config \
  -H "Content-Type: application/json" \
  -d '{"host":"localhost","port":3306,"username":"root","password":"password","database":"gs1"}'
```

✅ **Database Initialized**
```bash
curl -X POST http://localhost:9000/api/init-db
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| 400 "Gateway not APPROVED" | Complete Step 6 (Admin Approval) first |
| 404 "Entity not found" | Verify entity_id from Step 1 |
| 409 "Duplicate gateway_code" | Use unique gateway_code for each server |
| 500 "Database error" | Check `/api/save-db-config` and `/api/init-db` |

---

## File Organization

```
global_server/
├─ gs1.py                                    [Backend - 41 endpoints]
├─ schema.sql                                [Database schema]
├─ index.html                                [Frontend UI]
│
├─ Documentation/
│  ├─ QUICK_REFERENCE_FLOW.md               [START HERE - 1 page]
│  ├─ TEST_COMMANDS.md                      [Copy & paste commands]
│  ├─ SECURITY_SERVER_REGISTRATION_FLOW.md  [Complete guide]
│  ├─ FULL_CRUD_API_REFERENCE.md            [All CRUD operations]
│  ├─ ENDPOINT_REFERENCE.md                 [All HTTP endpoints]
│  └─ CRUD_IMPLEMENTATION_SUMMARY.md        [Implementation details]
```

---

## Development Workflow

### For First-Time Users
1. Read: [QUICK_REFERENCE_FLOW.md](QUICK_REFERENCE_FLOW.md)
2. Try: [TEST_COMMANDS.md](TEST_COMMANDS.md)
3. Explore: [SECURITY_SERVER_REGISTRATION_FLOW.md](SECURITY_SERVER_REGISTRATION_FLOW.md)

### For API Developers
1. Review: [ENDPOINT_REFERENCE.md](ENDPOINT_REFERENCE.md)
2. Reference: [FULL_CRUD_API_REFERENCE.md](FULL_CRUD_API_REFERENCE.md)
3. Implement: Custom clients/integrations

### For System Administrators
1. Understand: [QUICK_REFERENCE_FLOW.md](QUICK_REFERENCE_FLOW.md)
2. Execute: [TEST_COMMANDS.md](TEST_COMMANDS.md)
3. Monitor: Check endpoints for status verification

---

## API Server Details

**Backend**: FastAPI on port 9000
```bash
python gs1.py
# Server starts on http://0.0.0.0:9000
```

**Database**: MySQL on localhost:3306
```
Database: gs1
Tables: 7 (entities, network_config, server_keys, 
            certificate_requests, certificates, 
            registration_log, global_directory)
```

**Total Endpoints**: 41
- 3 database setup endpoints
- 38 CRUD endpoints (5-6 per table)

---

## Summary

✅ **All 7 steps documented**
✅ **Ready-to-use test commands provided**
✅ **Complete CRUD coverage**
✅ **Auto-actions implemented**
✅ **Audit trail maintained**
✅ **Progressive trust model**

**Status**: Production Ready 🚀

