# 🔐 CSR Validation & Troubleshooting Guide

## ❌ Error: "error parsing asn1 value: ParseError { kind: ShortData }"

This means **the CSR is corrupted or incomplete**.

---

## ✅ Solution: Generate a Valid Test CSR

### Quick Method - Run Generation Script

```bash
python generate_test_csr.py
```

This will:
- ✅ Generate valid RSA private key
- ✅ Create valid CSR
- ✅ Verify CSR integrity
- ✅ Show API request format
- ✅ Save files for reuse

---

## 🔧 Manual CSR Generation

If you want to generate CSR manually:

### Step 1: Generate Private Key
```bash
openssl genrsa -out my_private_key.pem 2048
```

### Step 2: Generate CSR
```bash
openssl req -new \
  -key my_private_key.pem \
  -out my_csr.pem \
  -subj "/C=EE/ST=Harjumaa/L=Tallinn/O=MyOrg/CN=TEST_GW001"
```

### Step 3: Verify CSR is Valid
```bash
openssl req -in my_csr.pem -text -noout
```

**Output should show:**
```
Certificate Request:
    Data:
        Version: 1 (0x0)
        Subject: C=EE, ST=Harjumaa, L=Tallinn, O=MyOrg, CN=TEST_GW001
        Public Key Algorithm: rsaEncryption
        ...
```

---

## 📋 CSR Format Requirements

Your CSR **MUST**:

✅ Start with:
```
-----BEGIN CERTIFICATE REQUEST-----
```

✅ End with:
```
-----END CERTIFICATE REQUEST-----
```

✅ Contain **complete** Base64 encoded data between markers

✅ **NOT** be truncated or have missing data

---

## 🔍 Verify CSR Format

Check if your CSR is valid:

```bash
# Show CSR details
openssl req -in your_csr.pem -text -noout

# Check if CSR is readable
openssl req -in your_csr.pem -noout -verify

# Both should succeed without errors
```

---

## ❌ Common CSR Issues

### Issue 1: Missing Data
```
❌ -----END CERTIFICATE REQUEST-----
   (data cuts off before this)

✅ Generate new CSR properly
```

### Issue 2: Wrong Format
```
❌ -----BEGIN CERTIFICATE-----  (wrong type)
✅ -----BEGIN CERTIFICATE REQUEST-----
```

### Issue 3: Escaped Newlines Not Decoded
```
❌ csr_pem: "-----BEGIN...\\n...\\n-----END..."  (literal \n)
✅ csr_pem: "-----BEGIN...\n...\n-----END..."  (actual newlines)
```

---

## 📊 Valid CSR Example

Here's a **complete valid CSR**:

```
-----BEGIN CERTIFICATE REQUEST-----
MIICqDCCAZQCAQAwXzELMAkGA1UEBhMCRUUxETAPBgNVBAgMCEhhcmp1bWFhMREw
DwYDVQQHDAhUYWxsaW5uMRAwDgYDVQQKDAdUZXN0T3JnMRQwEgYDVQQDDAtURVNU
X0dXMDAxCjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOGd1UuSSXHb
N8X5+xMShmyJS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fh6XAMPLECAwEAAaA2
MDAw
-----END CERTIFICATE REQUEST-----
```

---

## 🧪 Test Your CSR

### Method 1: Using Python Script
```bash
python generate_test_csr.py
```

### Method 2: Send to CA Service
```bash
curl -X POST http://localhost:9002/api/certificates/sign-csr \
  -H "Content-Type: application/json" \
  -d '{
    "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
    "server_id": "TEST_GW001",
    "cert_type": "auth"
  }'
```

---

## ✨ Expected Response (Success)

```json
{
  "status": "success",
  "certificate_pem": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
  "certificate_id": "550e8400-e29b-41d4-a716-446655440000",
  "server_id": "TEST_GW001",
  "certificate_type": "auth",
  "issued_date": "2026-04-16T10:30:00+00:00",
  "expiry_date": "2027-04-16T10:30:00+00:00",
  "thumbprint": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "message": "CSR signed successfully (auth certificate)"
}
```

---

## ⚠️ Error Response Examples

### Error 1: Invalid CSR Format
```json
{
  "detail": "Invalid CSR: CSR must start with '-----BEGIN CERTIFICATE REQUEST-----'"
}
```

### Error 2: Empty CSR
```json
{
  "detail": "Invalid CSR: csr_pem cannot be empty"
}
```

### Error 3: Corrupted CSR
```json
{
  "detail": "Invalid CSR: error parsing asn1 value: ParseError { kind: ShortData }"
}
```

⚠️ **Use `generate_test_csr.py` to create a valid CSR!**

---

## 🎯 Step-by-Step: Fix Your CSR

1. **Delete invalid CSR**
   ```bash
   rm test_keys/test_csr.pem
   ```

2. **Generate new valid CSR**
   ```bash
   python generate_test_csr.py
   ```

3. **Get the CSR content**
   ```bash
   cat test_keys/test_csr.pem
   ```

4. **Copy to your request (include full content)**
   ```json
   {
     "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\n[FULL CSR DATA]\n-----END CERTIFICATE REQUEST-----",
     "server_id": "TEST_GW001",
     "cert_type": "auth"
   }
   ```

5. **Send to CA Service**
   ```bash
   python -c "
   import requests, json
   with open('test_keys/sign_csr_request.json') as f:
       payload = json.load(f)
   resp = requests.post('http://localhost:9002/api/certificates/sign-csr', json=payload)
   print(resp.json())
   "
   ```

---

## 📚 References

- [OpenSSL CSR Documentation](https://www.openssl.org/docs/manmaster/man1/openssl-req.html)
- [X.509 Certificate Format](https://en.wikipedia.org/wiki/X.509)
- [Certificate Signing Request Spec](https://tools.ietf.org/html/rfc2986)

---

## 🚀 Quick Command Reference

| Task | Command |
|------|---------|
| Generate Valid CSR | `python generate_test_csr.py` |
| Show CSR Details | `openssl req -in csr.pem -text -noout` |
| Verify CSR Signature | `openssl req -in csr.pem -noout -verify` |
| Create New Key | `openssl genrsa -out key.pem 2048` |
| Extract Public Key | `openssl req -in csr.pem -noout -pubkey` |

---

## ✅ Validation Checklist

Before sending CSR to CA Service:

- [ ] CSR file is not empty
- [ ] CSR starts with `-----BEGIN CERTIFICATE REQUEST-----`
- [ ] CSR ends with `-----END CERTIFICATE REQUEST-----`
- [ ] No truncated or missing data
- [ ] Valid Base64 encoding
- [ ] `openssl req -in csr.pem -noout -verify` succeeds
- [ ] Certificate Manager initialized
- [ ] CA Service running on port 9002

---

## 🎉 Ready to Sign!

Once CSR is valid:

```bash
# Send to CA and get certificate
python generate_test_csr.py  # Follow the curl command shown
```

You'll get back a signed .crt file ready to use! 🔐

