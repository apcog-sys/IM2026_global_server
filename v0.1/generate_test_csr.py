#!/usr/bin/env python3
"""
Generate a valid Certificate Signing Request (CSR) for testing
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
OUTPUT_DIR = Path("./test_keys")
OUTPUT_DIR.mkdir(exist_ok=True)

KEY_FILE = OUTPUT_DIR / "test_rsa_key.pem"
CSR_FILE = OUTPUT_DIR / "test_csr.pem"

def generate_key_and_csr():
    """Generate RSA private key and CSR"""
    
    print("\n" + "="*60)
    print("  Generate Valid CSR for Testing")
    print("="*60 + "\n")
    
    # Step 1: Generate RSA private key
    print("▸ Step 1: Generate 2048-bit RSA private key...")
    try:
        subprocess.run([
            "openssl", "genrsa", "-out", str(KEY_FILE), "2048"
        ], capture_output=True, check=True)
        print(f"  ✅ Private key saved: {KEY_FILE}\n")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e}")
        print("  Make sure OpenSSL is installed: https://slproweb.com/products/Win32OpenSSL.html")
        return None
    
    # Step 2: Generate CSR
    print("▸ Step 2: Generate Certificate Signing Request...")
    try:
        subprocess.run([
            "openssl", "req",
            "-new",
            "-key", str(KEY_FILE),
            "-out", str(CSR_FILE),
            "-subj", "/C=EE/ST=Harjumaa/L=Tallinn/O=TestOrg/CN=TEST_GW001"
        ], capture_output=True, check=True)
        print(f"  ✅ CSR saved: {CSR_FILE}\n")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e}")
        return None
    
    # Step 3: Display CSR content
    print("▸ Step 3: Display CSR content...")
    with open(CSR_FILE, "r") as f:
        csr_content = f.read()
    
    print(f"  CSR Length: {len(csr_content)} characters\n")
    print("CSR Content:")
    print(csr_content)
    
    # Step 4: Verify CSR
    print("\n▸ Step 4: Verify CSR integrity...")
    try:
        result = subprocess.run([
            "openssl", "req",
            "-in", str(CSR_FILE),
            "-text",
            "-noout"
        ], capture_output=True, text=True, check=True)
        print("  ✅ CSR is valid!\n")
        print("CSR Details:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ CSR verification failed: {e}")
        return None
    
    # Step 5: Create API request JSON
    print("\n▸ Step 5: Create API request JSON...")
    api_request = {
        "server_id": "TEST_GW001",
        "cert_type": "auth",
        "csr_pem": csr_content
    }
    
    request_file = OUTPUT_DIR / "sign_csr_request.json"
    with open(request_file, "w") as f:
        json.dump(api_request, f, indent=2)
    
    print(f"  ✅ Request saved: {request_file}\n")
    
    # Step 6: Display curl command
    print("\n" + "="*60)
    print("  Send CSR to CA Service")
    print("="*60 + "\n")
    
    print("Using cURL:")
    curl_cmd = f"""curl -X POST http://localhost:9002/api/certificates/sign-csr \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(api_request, indent=2)}'"""
    print(curl_cmd)
    
    print("\n\nUsing Python Requests:")
    python_code = """import requests
import json

with open("test_keys/sign_csr_request.json", "r") as f:
    payload = json.load(f)

response = requests.post(
    "http://localhost:9002/api/certificates/sign-csr",
    json=payload
)

print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Save certificate
if response.status_code == 201:
    cert_pem = response.json()["certificate_pem"]
    with open("test_keys/signed_cert.crt", "w") as f:
        f.write(cert_pem)
    print("✅ Certificate saved to: test_keys/signed_cert.crt")
"""
    print(python_code)
    
    print("\n" + "="*60)
    print("  Files Generated")
    print("="*60 + "\n")
    for file in OUTPUT_DIR.glob("*"):
        size = file.stat().st_size
        print(f"  • {file.name} ({size} bytes)")
    
    print("\n\n✅ CSR generation complete!")
    print("\nNext steps:")
    print("  1. Make sure CA Service is running: python CA_management/ca_service.py")
    print("  2. Send CSR to CA: curl or python code above")
    print("  3. Receive signed certificate")
    print("\n")

if __name__ == "__main__":
    generate_key_and_csr()
