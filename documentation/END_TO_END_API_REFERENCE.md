# 🟢 END-TO-END SECURITY SERVER REGISTRATION FLOW - Complete API Guide

## Overview

Progressive trust model with 7 steps for secure security server registration:

```
STEP 1: Entity Creation
   ↓
STEP 2: Security Server Registers (PENDING)
   ↓
STEP 3: Upload AUTH & SIGN Public Keys
   ↓
STEP 4: Submit CSRs (PENDING)
   ↓
STEP 5: CA Signs Certificates (ACTIVE)
   ↓
STEP 6: Admin Approval (APPROVED)
   ↓
STEP 7: Publish to Global Directory (DISCOVERABLE)
```

---

## Initial Setup

### 1. Save Database Configuration

```bash
curl -X POST http://localhost:9000/api/save-db-config \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "your_password",
    "database": "gs1"
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Database configuration saved",
  "config": {
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "database": "gs1"
  }
}
```

### 2. Initialize Database Tables

```bash
curl -X POST http://localhost:9000/api/init-db
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Database tables initialized successfully - NEW SCHEMA (7 tables)"
}
```

---

## 🟢 STEP 1: Entity Creation (Admin)

### Endpoint: Create Organization

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

**Request Body:**
```json
{
  "entity_code": "ORG1",
  "entity_name": "My Organization",
  "entity_type": "Organization",
  "status": "ACTIVE"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Entity created successfully",
  "entity": {
    "entity_id": 1,
    "entity_code": "ORG1",
    "entity_name": "My Organization",
    "entity_type": "Organization",
    "status": "ACTIVE"
  }
}
```

### List All Entities

```bash
curl http://localhost:9000/api/entities
```

**Response:**
```json
{
  "status": "success",
  "entities": [
    {
      "entity_id": 1,
      "entity_code": "ORG1",
      "entity_name": "My Organization",
      "entity_type": "Organization",
      "status": "ACTIVE",
      "created_at": "2026-04-10 10:00:00"
    }
  ],
  "total": 1
}
```

---

## 🟢 STEP 2: Security Server Registers

### Endpoint: Register Gateway (PENDING STATUS)

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

**Request Body:**
```json
{
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
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Security server registered - PENDING APPROVAL",
  "network_config": {
    "id": 1,
    "gateway_code": "GW001",
    "entity_id": 1,
    "host": "192.168.1.100",
    "port": 9001,
    "status": "PENDING",
    "created_at": "2026-04-10T10:05:00"
  }
}
```

### List All Network Configurations

```bash
curl http://localhost:9000/api/network-config
```

### Get Specific Gateway

```bash
curl http://localhost:9000/api/network-config/GW001
```

---

## 🟢 STEP 3: Upload AUTH & SIGN Public Keys

### Endpoint: Upload AUTH Public Key

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_type": "AUTH",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "AUTH public key uploaded successfully",
  "server_key": {
    "key_id": 1,
    "gateway_code": "GW001",
    "key_type": "AUTH",
    "created_at": "2026-04-10T10:10:00"
  }
}
```

### Endpoint: Upload SIGN Public Key

```bash
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_type": "SIGN",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "SIGN public key uploaded successfully",
  "server_key": {
    "key_id": 2,
    "gateway_code": "GW001",
    "key_type": "SIGN",
    "created_at": "2026-04-10T10:11:00"
  }
}
```

### Get Server Keys

```bash
curl http://localhost:9000/api/server-keys/GW001
```

**Response:**
```json
{
  "status": "success",
  "gateway_code": "GW001",
  "keys": [
    {
      "key_id": 1,
      "gateway_code": "GW001",
      "key_type": "AUTH",
      "created_at": "2026-04-10 10:10:00"
    },
    {
      "key_id": 2,
      "gateway_code": "GW001",
      "key_type": "SIGN",
      "created_at": "2026-04-10 10:11:00"
    }
  ],
  "total": 2
}
```

---

## 🟢 STEP 4: Submit CSRs (PENDING SIGNING)

### Endpoint: Submit AUTH CSR

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

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "AUTH CSR submitted - PENDING SIGNING",
  "certificate_request": {
    "csr_id": 1,
    "gateway_code": "GW001",
    "cert_type": "AUTH",
    "status": "PENDING",
    "requested_at": "2026-04-10T10:15:00"
  }
}
```

### Endpoint: Submit SIGN CSR

```bash
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 2,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\nMIICqDCCAZQCAQAwXzELMAkGA1UEBhMCVVM...\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "SIGN"
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "SIGN CSR submitted - PENDING SIGNING",
  "certificate_request": {
    "csr_id": 2,
    "gateway_code": "GW001",
    "cert_type": "SIGN",
    "status": "PENDING",
    "requested_at": "2026-04-10T10:16:00"
  }
}
```

### List All CSR Requests

```bash
curl http://localhost:9000/api/certificate-requests
```

### List Pending CSRs

```bash
curl "http://localhost:9000/api/certificate-requests?status=PENDING"
```

---

## 🟢 STEP 5: CA Signs Certificates (ACTIVE)

### Endpoint: Store AUTH Certificate

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

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "AUTH certificate signed and stored - ACTIVE",
  "certificate": {
    "cert_id": 1,
    "gateway_code": "GW001",
    "cert_type": "AUTH",
    "status": "ACTIVE",
    "valid_to": "2027-04-10T10:20:00",
    "created_at": "2026-04-10T10:20:00"
  }
}
```

### Endpoint: Store SIGN Certificate

```bash
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 2,
    "cert_type": "SIGN",
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDBTCCAe2gAwIBAgIUgKyQaJ9c2M8...\n-----END CERTIFICATE-----",
    "issued_by": "CA Authority",
    "valid_from": "2026-04-10T10:21:00",
    "valid_to": "2027-04-10T10:21:00"
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "SIGN certificate signed and stored - ACTIVE",
  "certificate": {
    "cert_id": 2,
    "gateway_code": "GW001",
    "cert_type": "SIGN",
    "status": "ACTIVE",
    "valid_to": "2027-04-10T10:21:00",
    "created_at": "2026-04-10T10:21:00"
  }
}
```

### Get Certificates for Gateway

```bash
curl http://localhost:9000/api/certificates/GW001
```

---

## 🟢 STEP 6: Admin Approval

### Endpoint: Approve Gateway Registration

```bash
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "action": "APPROVED",
    "performed_by": "admin@example.com",
    "remarks": "Security gateway verified and approved for production"
  }'
```

**Request Body:**
```json
{
  "gateway_code": "GW001",
  "action": "APPROVED",
  "performed_by": "admin@example.com",
  "remarks": "Security gateway verified and approved for production"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Registration action logged: APPROVED",
  "registration_log": {
    "log_id": 1,
    "gateway_code": "GW001",
    "action": "APPROVED",
    "performed_by": "admin@example.com",
    "created_at": "2026-04-10T10:25:00"
  }
}
```

### Get Registration Log

```bash
curl http://localhost:9000/api/registration-log/GW001
```

**Response:**
```json
{
  "status": "success",
  "gateway_code": "GW001",
  "logs": [
    {
      "log_id": 1,
      "gateway_code": "GW001",
      "action": "SUBMITTED",
      "performed_by": "security_server",
      "created_at": "2026-04-10 10:05:00"
    },
    {
      "log_id": 2,
      "gateway_code": "GW001",
      "action": "APPROVED",
      "performed_by": "admin@example.com",
      "remarks": "Security gateway verified and approved for production",
      "created_at": "2026-04-10 10:25:00"
    }
  ],
  "total": 2
}
```

---

## 🟢 STEP 7: Publish to Global Directory (DISCOVERABLE)

### Endpoint: Publish Gateway to Global Directory

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

**Request Body:**
```json
{
  "entity_code": "ORG1",
  "gateway_code": "GW001",
  "service_url": "https://gateway1.example.com:9001",
  "auth_cert_id": 1,
  "sign_cert_id": 2
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Gateway published to Global Directory - VISIBLE SYSTEM-WIDE",
  "global_directory_entry": {
    "directory_id": 1,
    "entity_code": "ORG1",
    "gateway_code": "GW001",
    "service_url": "https://gateway1.example.com:9001",
    "status": "ACTIVE",
    "created_at": "2026-04-10T10:30:00"
  }
}
```

### Endpoint: Discover All Published Servers

```bash
curl http://localhost:9000/api/global-directory
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Global Directory - Discoverable Servers",
  "global_directory": [
    {
      "directory_id": 1,
      "entity_code": "ORG1",
      "gateway_code": "GW001",
      "entity_name": "My Organization",
      "host": "192.168.1.100",
      "port": 9001,
      "service_url": "https://gateway1.example.com:9001",
      "status": "ACTIVE",
      "created_at": "2026-04-10 10:30:00"
    }
  ],
  "total": 1
}
```

### List Only Active Servers

```bash
curl "http://localhost:9000/api/global-directory?status=ACTIVE"
```

---

## 📋 Complete End-to-End Bash Script

```bash
#!/bin/bash

echo "=== STEP 1: Configure Database ==="
curl -X POST http://localhost:9000/api/save-db-config \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "your_password",
    "database": "gs1"
  }'

echo -e "\n=== STEP 2: Initialize Database Tables ==="
curl -X POST http://localhost:9000/api/init-db

echo -e "\n=== STEP 3: Create Entity/Organization ==="
curl -X POST http://localhost:9000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "ORG1",
    "entity_name": "My Organization",
    "entity_type": "Organization",
    "status": "ACTIVE"
  }'

echo -e "\n=== STEP 4: Register Security Gateway ==="
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

echo -e "\n=== STEP 5: Upload AUTH Key ==="
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_type": "AUTH",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
  }'

echo -e "\n=== STEP 6: Upload SIGN Key ==="
curl -X POST http://localhost:9000/api/server-keys \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_type": "SIGN",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
  }'

echo -e "\n=== STEP 7: Submit AUTH CSR ==="
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 1,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "AUTH"
  }'

echo -e "\n=== STEP 8: Submit SIGN CSR ==="
curl -X POST http://localhost:9000/api/certificate-requests \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 2,
    "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
    "cert_type": "SIGN"
  }'

echo -e "\n=== STEP 9: Store AUTH Certificate (CA Signed) ==="
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 1,
    "cert_type": "AUTH",
    "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "issued_by": "CA Authority",
    "valid_from": "2026-04-10T10:20:00",
    "valid_to": "2027-04-10T10:20:00"
  }'

echo -e "\n=== STEP 10: Store SIGN Certificate (CA Signed) ==="
curl -X POST http://localhost:9000/api/certificates \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "key_id": 2,
    "cert_type": "SIGN",
    "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "issued_by": "CA Authority",
    "valid_from": "2026-04-10T10:21:00",
    "valid_to": "2027-04-10T10:21:00"
  }'

echo -e "\n=== STEP 11: Admin Approval ==="
curl -X POST http://localhost:9000/api/registration-log \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_code": "GW001",
    "action": "APPROVED",
    "performed_by": "admin@example.com",
    "remarks": "Gateway approved"
  }'

echo -e "\n=== STEP 12: Publish to Global Directory ==="
curl -X POST http://localhost:9000/api/global-directory \
  -H "Content-Type: application/json" \
  -d '{
    "entity_code": "ORG1",
    "gateway_code": "GW001",
    "service_url": "https://gateway1.example.com:9001",
    "auth_cert_id": 1,
    "sign_cert_id": 2
  }'

echo -e "\n=== Discover Published Servers ==="
curl http://localhost:9000/api/global-directory

echo -e "\n✓ Complete!"
```

---

## Database Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `entities` | Organizations | entity_code, entity_name, status |
| `network_config` | Security Servers | gateway_code, status (PENDING→APPROVED) |
| `server_keys` | AUTH & SIGN Keys | key_type (AUTH/SIGN), public_key |
| `certificate_requests` | CSRs | csr_data, status (PENDING→SIGNED) |
| `certificates` | Signed Certs | cert_type, certificate, valid_to |
| `registration_log` | Audit Trail | action (SUBMITTED/APPROVED/REJECTED) |
| `global_directory` | Discovery | gateway_code, service_url, status |

---

## Status Progression

```
network_config.status:
  PENDING → APPROVED → (REJECTED)
                 ↑
                 └─ Once certificates are ACTIVE
                    and admin approves

certificate_requests.status:
  PENDING → SIGNED → (REJECTED)

certificates.status:
  ACTIVE → EXPIRED / REVOKED
```

---

##Notes

- All timestamps are ISO 8601 format
- All primary keys are auto-incremented
- Foreign keys ensure data integrity
- CORS enabled for frontend on port 8000
- Database: gs1 (MySQL)

