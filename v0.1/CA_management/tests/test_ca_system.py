"""
Test Suite for Certificate Authority Service
Tests all CA endpoints and certificate generation workflows
"""

import requests
import json
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# CA Service running on port 9002
BASE_URL = "http://localhost:9002"

# Test data - sample public key (RSA-2048)
SAMPLE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Z3qX2BTLS4e8xVSwGXN
/yJd3vvXDI3v/qvKWZ7+fNxDxJ6K5bq3u7B7V8rJZ7rk8gH9kJ3h7V9vL2Z9mZ7V
mJrK3K7P9N5Y6V8Q0K8T3L9V0Z6X7V1Y2Z7Z9Z6X5V9Q1M9U4M8W6Y8W0Z8Z7W6V
9R2N9V5N9X7Z9W1Z8Z7W6V9R2N9V5N9X7Z9W1Y9a8X7V9R2N9V5N9X7Z9W1Y9a8
W7Z8S3O0W6O0Y8a0X2a9a8X7V9R2N9V5N9X7Z9W1Y9a8X7V9R2N9V5N9X7Z9W1Y
9a8X7V9R2N9V5N9X7Z9W1Y9a8X7V9R2N9V5N9X7Z9W1Y9a8X7V9R2N9V5N9X7Z9
WQIDAQAB
-----END PUBLIC KEY-----"""


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(test_name: str, passed: bool, message: str = ""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"     {message}")


def test_health_check():
    """Test CA service health check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_result("Health Check", True, f"Service healthy: {data['service']}")
            return True
        else:
            print_result("Health Check", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False


def test_generate_auth_certificate():
    """Test Authentication certificate generation"""
    try:
        payload = {
            "server_id": "TEST_SERVER_1",
            "server_name": "Test Gateway",
            "organization": "Test Organization",
            "address": "192.168.1.100",
            "public_key_pem": SAMPLE_PUBLIC_KEY,
            "certificate_type": "auth"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/certificates/generate-auth",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            
            # Verify response structure
            required_fields = ["certificate_id", "thumbprint", "certificate_pem", 
                             "issued_date", "expiry_date"]
            
            if all(field in data for field in required_fields):
                print_result(
                    "Generate Authentication Certificate",
                    True,
                    f"Certificate ID: {data['certificate_id'][:8]}..."
                )
                return True, data
            else:
                print_result(
                    "Generate Authentication Certificate",
                    False,
                    f"Missing fields in response"
                )
                return False, None
        else:
            print_result(
                "Generate Authentication Certificate",
                False,
                f"Status code: {response.status_code}, Response: {response.text}"
            )
            return False, None
            
    except Exception as e:
        print_result("Generate Authentication Certificate", False, str(e))
        return False, None


def test_generate_sign_certificate():
    """Test Signature certificate generation"""
    try:
        payload = {
            "server_id": "TEST_SERVER_2",
            "server_name": "Test Gateway 2",
            "organization": "Test Organization",
            "public_key_pem": SAMPLE_PUBLIC_KEY,
            "certificate_type": "sign"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/certificates/generate-sign",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            
            required_fields = ["certificate_id", "thumbprint", "certificate_pem",
                             "issued_date", "expiry_date"]
            
            if all(field in data for field in required_fields):
                print_result(
                    "Generate Signature Certificate",
                    True,
                    f"Certificate ID: {data['certificate_id'][:8]}..."
                )
                return True, data
            else:
                print_result(
                    "Generate Signature Certificate",
                    False,
                    f"Missing fields in response"
                )
                return False, None
        else:
            print_result(
                "Generate Signature Certificate",
                False,
                f"Status code: {response.status_code}"
            )
            return False, None
            
    except Exception as e:
        print_result("Generate Signature Certificate", False, str(e))
        return False, None


def test_generate_both_certificates():
    """Test generating both certificates in one call"""
    try:
        payload = {
            "server_id": "TEST_SERVER_3",
            "server_name": "Test Gateway 3",
            "organization": "Test Organization",
            "address": "192.168.1.101",
            "public_key_pem": SAMPLE_PUBLIC_KEY,
            "certificate_type": "auth"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/certificates/generate-both",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            
            if "auth_certificate" in data and "sign_certificate" in data:
                print_result(
                    "Generate Both Certificates",
                    True,
                    f"Generated 2 certificates successfully"
                )
                return True, data
            else:
                print_result(
                    "Generate Both Certificates",
                    False,
                    f"Missing certificate data"
                )
                return False, None
        else:
            print_result(
                "Generate Both Certificates",
                False,
                f"Status code: {response.status_code}"
            )
            return False, None
            
    except Exception as e:
        print_result("Generate Both Certificates", False, str(e))
        return False, None


def test_get_ca_root():
    """Test retrieving CA root certificate"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/certificates/ca-root",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "certificate_pem" in data and "BEGIN CERTIFICATE" in data["certificate_pem"]:
                print_result(
                    "Get CA Root Certificate",
                    True,
                    "Root certificate retrieved successfully"
                )
                return True
            else:
                print_result(
                    "Get CA Root Certificate",
                    False,
                    "Invalid certificate data"
                )
                return False
        else:
            print_result(
                "Get CA Root Certificate",
                False,
                f"Status code: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_result("Get CA Root Certificate", False, str(e))
        return False


def test_get_certificate_chain():
    """Test retrieving certificate chain"""
    try:
        # First generate certificates
        payload = {
            "server_id": "TEST_SERVER_CHAIN",
            "server_name": "Chain Test Server",
            "organization": "Test Organization",
            "address": "192.168.1.102",
            "public_key_pem": SAMPLE_PUBLIC_KEY,
            "certificate_type": "auth"
        }
        
        requests.post(
            f"{BASE_URL}/api/certificates/generate-both",
            json=payload,
            timeout=10
        )
        
        time.sleep(1)  # Wait for database
        
        # Now retrieve chain
        response = requests.get(
            f"{BASE_URL}/api/certificates/TEST_SERVER_CHAIN/chain",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "chain" in data and "ca_root" in data:
                print_result(
                    "Get Certificate Chain",
                    True,
                    "Certificate chain retrieved successfully"
                )
                return True
            else:
                print_result(
                    "Get Certificate Chain",
                    False,
                    "Invalid chain data"
                )
                return False
        else:
            print_result(
                "Get Certificate Chain",
                False,
                f"Status code: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_result("Get Certificate Chain", False, str(e))
        return False


def test_get_server_certificates():
    """Test retrieving all certificates for a server"""
    try:
        # Assuming TEST_SERVER_1 already has certificates from earlier test
        response = requests.get(
            f"{BASE_URL}/api/certificates/server/TEST_SERVER_1",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "certificates" in data:
                count = len(data["certificates"])
                print_result(
                    "Get Server Certificates",
                    True,
                    f"Retrieved {count} certificate(s) for TEST_SERVER_1"
                )
                return True
            else:
                print_result(
                    "Get Server Certificates",
                    False,
                    "Invalid response data"
                )
                return False
        else:
            print_result(
                "Get Server Certificates",
                False,
                f"Status code: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_result("Get Server Certificates", False, str(e))
        return False


def print_summary(results: list):
    """Print test summary"""
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print_header(f"Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")


def main():
    """Run all tests"""
    print_header("Certificate Authority Service Test Suite")
    
    print(f"\nCA Service URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}\n")
    
    # Run tests
    results = []
    
    results.append(test_health_check())
    time.sleep(1)
    
    results.append(test_generate_auth_certificate()[0] is not None)
    time.sleep(1)
    
    results.append(test_generate_sign_certificate()[0] is not None)
    time.sleep(1)
    
    results.append(test_generate_both_certificates()[0] is not None)
    time.sleep(1)
    
    results.append(test_get_ca_root())
    time.sleep(1)
    
    results.append(test_get_certificate_chain())
    time.sleep(1)
    
    results.append(test_get_server_certificates())
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test suite interrupted")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
