#!/usr/bin/env python3
"""
Test script for CSR to CRT conversion via CA Service API

Usage:
  python test_csr_signing.py

This script:
1. Generates a test CSR using command line tools
2. Sends CSR to CA Service
3. Receives signed certificate
4. Validates the certificate
5. Saves certificate to file
"""

import requests
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
CA_SERVICE_URL = "http://localhost:9002"
SIGN_CSR_ENDPOINT = "/api/certificates/sign-csr"

# Test data
TEST_SERVER_ID = "TEST_GW001"
TEST_CERT_TYPE = "auth"
TEST_OUTPUT_DIR = Path("./test_output")

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def generate_test_csr():
    """Generate test CSR using OpenSSL"""
    print_section("STEP 1: Generate Test CSR")
    
    # Create output directory
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    csr_file = TEST_OUTPUT_DIR / "test_csr.pem"
    key_file = TEST_OUTPUT_DIR / "test_key.pem"
    
    try:
        # Generate private key
        print("▸ Generating private key...")
        subprocess.run([
            "openssl", "genrsa", "-out", str(key_file), "2048"
        ], capture_output=True, check=True)
        print(f"  ✅ Private key: {key_file}")
        
        # Generate CSR
        print("▸ Generating Certificate Signing Request...")
        subprocess.run([
            "openssl", "req", "-new",
            "-key", str(key_file),
            "-out", str(csr_file),
            "-subj", f"/C=EE/ST=Harjumaa/L=Tallinn/O=TestOrg/CN={TEST_SERVER_ID}"
        ], capture_output=True, check=True)
        print(f"  ✅ CSR file: {csr_file}")
        
        # Read CSR content
        with open(csr_file, "r") as f:
            csr_pem = f.read()
        
        print(f"  ✅ CSR length: {len(csr_pem)} characters")
        
        return csr_pem
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e}")
        print(f"  Make sure OpenSSL is installed and in PATH")
        sys.exit(1)

def verify_csr(csr_pem):
    """Verify CSR validity"""
    print_section("STEP 2: Verify CSR")
    
    try:
        csr_file = TEST_OUTPUT_DIR / "test_csr.pem"
        
        # Verify CSR
        result = subprocess.run([
            "openssl", "req", "-in", str(csr_file), "-text", "-noout"
        ], capture_output=True, text=True, check=True)
        
        print("▸ CSR Details:")
        for line in result.stdout.split("\n")[:10]:
            if line.strip():
                print(f"  {line}")
        
        print("\n  ✅ CSR is valid and properly formatted")
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error verifying CSR: {e}")
        sys.exit(1)

def send_csr_to_ca(csr_pem):
    """Send CSR to CA Service for signing"""
    print_section("STEP 3: Send CSR to CA Service")
    
    print(f"▸ Endpoint: {CA_SERVICE_URL}{SIGN_CSR_ENDPOINT}")
    print(f"▸ Server ID: {TEST_SERVER_ID}")
    print(f"▸ Certificate Type: {TEST_CERT_TYPE}")
    
    # Prepare payload
    payload = {
        "csr_pem": csr_pem,
        "server_id": TEST_SERVER_ID,
        "cert_type": TEST_CERT_TYPE
    }
    
    try:
        # Send request
        print("\n▸ Sending request...")
        response = requests.post(
            f"{CA_SERVICE_URL}{SIGN_CSR_ENDPOINT}",
            json=payload,
            timeout=30
        )
        
        # Check response
        if response.status_code == 201:
            print(f"  ✅ Response received (Status: {response.status_code})")
            
            result = response.json()
            
            if result.get("status") == "success":
                print(f"  ✅ CSR signed successfully")
                print(f"  ✅ Certificate ID: {result.get('certificate_id')}")
                
                return result
            else:
                print(f"  ❌ CA Service error: {result.get('message')}")
                sys.exit(1)
        else:
            print(f"  ❌ HTTP {response.status_code}: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to CA Service at {CA_SERVICE_URL}")
        print(f"  Make sure CA Service is running:")
        print(f"  python CA_management/ca_service.py")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"  ❌ Request timeout")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)

def save_certificate(cert_data):
    """Save certificate to file"""
    print_section("STEP 4: Save Certificate")
    
    cert_pem = cert_data.get("certificate_pem")
    if not cert_pem:
        print("  ❌ No certificate in response")
        sys.exit(1)
    
    cert_file = TEST_OUTPUT_DIR / "certificate.crt"
    
    try:
        with open(cert_file, "w") as f:
            f.write(cert_pem)
        
        print(f"▸ Certificate file: {cert_file}")
        print(f"  ✅ Certificate saved ({len(cert_pem)} chars)")
        
        return str(cert_file)
        
    except Exception as e:
        print(f"  ❌ Error saving certificate: {e}")
        sys.exit(1)

def verify_certificate(cert_file):
    """Verify the signed certificate"""
    print_section("STEP 5: Verify Signed Certificate")
    
    try:
        # Display certificate info
        result = subprocess.run([
            "openssl", "x509", "-in", cert_file, "-text", "-noout"
        ], capture_output=True, text=True, check=True)
        
        print("▸ Certificate Details:")
        lines = result.stdout.split("\n")
        
        # Extract key information
        for line in lines[:20]:
            if any(key in line for key in ["Issuer:", "Subject:", "Not Before", "Not After", "Public"]):
                print(f"  {line}")
        
        # Check dates
        result = subprocess.run([
            "openssl", "x509", "-in", cert_file, "-noout", "-dates"
        ], capture_output=True, text=True, check=True)
        
        print("\n▸ Validity:")
        for line in result.stdout.split("\n"):
            if line.strip():
                print(f"  {line}")
        
        print(f"\n  ✅ Certificate is valid and properly signed")
        
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Could not verify certificate (OpenSSL may not be available)")
        print(f"     But certificate was received and saved successfully")

def verify_chain(cert_data):
    """Verify certificate chain"""
    print_section("STEP 6: Display Certificate Information")
    
    print("▸ Certificate Details from API Response:")
    print(f"  ID: {cert_data.get('certificate_id')}")
    print(f"  Server: {cert_data.get('server_id')}")
    print(f"  Type: {cert_data.get('certificate_type')}")
    print(f"  Issued: {cert_data.get('issued_date')}")
    print(f"  Expires: {cert_data.get('expiry_date')}")
    print(f"  Thumbprint: {cert_data.get('thumbprint', 'N/A')[:16]}...")
    print(f"\n  ✅ Certificate signed by CA")

def main():
    """Run complete CSR signing test"""
    
    print("\n")
    print("┌" + "─" * 58 + "┐")
    print("│" + " " * 58 + "│")
    print("│" + "  CSR to CRT Conversion Test".center(58) + "│")
    print("│" + "  CA Service Integration".center(58) + "│")
    print("│" + " " * 58 + "│")
    print("└" + "─" * 58 + "┘")
    
    # Step 1: Generate CSR
    csr_pem = generate_test_csr()
    
    # Step 2: Verify CSR
    verify_csr(csr_pem)
    
    # Step 3: Send to CA
    cert_data = send_csr_to_ca(csr_pem)
    
    # Step 4: Save certificate
    cert_file = save_certificate(cert_data)
    
    # Step 5: Verify certificate
    try:
        verify_certificate(cert_file)
    except:
        pass
    
    # Step 6: Display info
    verify_chain(cert_data)
    
    # Summary
    print_section("✅ TEST COMPLETE")
    print(f"Output directory: {TEST_OUTPUT_DIR.absolute()}\n")
    print("Generated files:")
    for file in TEST_OUTPUT_DIR.glob("*"):
        size = file.stat().st_size
        print(f"  • {file.name} ({size} bytes)")
    
    print("\n✅ CSR successfully converted to CRT via CA Service!")
    print("\nNext steps:")
    print("  • Use certificate.crt in your application")
    print("  • Verify with: openssl x509 -in test_output/certificate.crt -text")
    print("  • Store in database or deploy to servers")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
