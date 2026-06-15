#!/usr/bin/env python3
"""
Quick test script to verify CA Integration workflow
Tests the complete flow: CSR → CA → CRT
"""

import requests
import json
import time

BASE_URL = "http://localhost:9000"
CA_URL = "http://localhost:9002"

print("=" * 70)
print("  CA Integration Test Suite")
print("=" * 70)

# Test 1: Check if services are running
print("\n[TEST 1] Checking if services are running...")
try:
    gs_health = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"  ✓ Global Server (9000): {gs_health.status_code} OK")
except:
    print(f"  ✗ Global Server (9000): NOT RUNNING")
    print(f"    Start with: python gs1.py")
    exit(1)

try:
    ca_health = requests.get(f"{CA_URL}/health", timeout=5)
    print(f"  ✓ CA Service (9002): {ca_health.status_code} OK")
except:
    print(f"  ✗ CA Service (9002): NOT RUNNING")
    print(f"    Start with: python CA_management/ca_service.py")
    exit(1)

# Test 2: Register CSR
print("\n[TEST 2] Registering CSR via Global Server...")

csr_payload = {
    "gateway_code": "TEST_GW_INTEGRATION",
    "key_id": 1,
    "cert_type": "AUTH",
    "csr_data": """-----BEGIN CERTIFICATE REQUEST-----
MIICqDCCAZQCAQAwXzELMAkGA1UEBhMCFUExFTATBgNVBAgMDFRlc3RUb3duLlVM
MRQwEgYDVQQHDAtUZXN0Q291bnRyeTEPMA0GA1UECgwGVGVzdENvMQswCQYDVQQD
DAJBVTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANGd1UuSSXHbN8X5
/xMShi5JS11yjjCQCu8KmhK0EnT+zIy4zqSiT816U8fhEXAMPLECAwEAAaA2MDAw
BgMCABAME1Rlc3RBcC5QbGFjZWhvbGRlcjELBgNVBAwEA1VTQzANBgkqhkiG9w0B
AQUFAAOCAQEA1Z3VS5JJcds3xfn/ExKGLklLBZqLpV2S7PLD1/Q2
-----END CERTIFICATE REQUEST-----"""
}

try:
    reg_response = requests.post(f"{BASE_URL}/api/certificate-requests", json=csr_payload)
    if reg_response.status_code == 201 or reg_response.status_code == 200:
        reg_data = reg_response.json()
        csr_id = reg_data.get("csr_id")
        print(f"  ✓ CSR Registered: CSR ID = {csr_id}")
    else:
        print(f"  ✗ CSR Registration failed: {reg_response.status_code}")
        print(f"    Response: {reg_response.text}")
        exit(1)
except Exception as e:
    print(f"  ✗ CSR Registration error: {e}")
    exit(1)

# Test 3: Get CRT from CSR
print(f"\n[TEST 3] Calling /api/certificate-requests/{csr_id}/get-crt...")

try:
    crt_response = requests.post(f"{BASE_URL}/api/certificate-requests/{csr_id}/get-crt")
    
    if crt_response.status_code == 200:
        crt_data = crt_response.json()
        print(f"  ✓ Certificate Generated Successfully!")
        print(f"    - Cert ID: {crt_data.get('cert_id')}")
        print(f"    - Gateway Code: {crt_data.get('gateway_code')}")
        print(f"    - Type: {crt_data.get('cert_type')}")
        print(f"    - Status: {crt_data.get('status')}")
        print(f"    - Message: {crt_data.get('message')}")
    else:
        print(f"  ✗ Get CRT failed: {crt_response.status_code}")
        print(f"    Response: {crt_response.text}")
        
except Exception as e:
    print(f"  ✗ Get CRT error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Verify CSR status is now SIGNED
print(f"\n[TEST 4] Verifying CSR status updated to SIGNED...")

try:
    csr_detail = requests.get(f"{BASE_URL}/api/certificate-requests/{csr_id}")
    if csr_detail.status_code == 200:
        csr_data = csr_detail.json().get("request", {})
        status = csr_data.get("status")
        print(f"  ✓ CSR Status: {status}")
        if status == "SIGNED":
            print(f"    ✓ Status correctly updated to SIGNED")
        else:
            print(f"    ✗ Status not updated (still: {status})")
    else:
        print(f"  ✗ Failed to get CSR details: {csr_detail.status_code}")
except Exception as e:
    print(f"  ✗ Error checking CSR status: {e}")

# Test 5: Verify certificate exists
print(f"\n[TEST 5] Checking if certificate was stored in database...")

try:
    certs_response = requests.get(f"{BASE_URL}/api/certificates")
    if certs_response.status_code == 200:
        certs_data = certs_response.json()
        cert_count = certs_data.get("total", 0)
        print(f"  ✓ Total Certificates in DB: {cert_count}")
        
        if cert_count > 0:
            certs = certs_data.get("certificates", [])
            latest_cert = certs[0] if certs else {}
            print(f"    - Latest Cert ID: {latest_cert.get('cert_id')}")
            print(f"    - Gateway Code: {latest_cert.get('gateway_code')}")
            print(f"    - Type: {latest_cert.get('cert_type')}")
            print(f"    - Status: {latest_cert.get('status')}")
    else:
        print(f"  ✗ Failed to get certificates: {certs_response.status_code}")
except Exception as e:
    print(f"  ✗ Error checking certificates: {e}")

print("\n" + "=" * 70)
print("  Test Complete! ✓")
print("=" * 70)
print("\nNext Steps:")
print("  1. Open http://localhost:8000 in browser")
print("  2. Go to Certificate Management → CSR Registration")
print("  3. See your CSR with 'Get CRT' button")
print("  4. Or go to Certificates tab to see the generated CRT")
print("=" * 70)
