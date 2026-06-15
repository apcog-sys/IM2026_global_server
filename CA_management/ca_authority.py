"""
Public Key Infrastructure (PKI) Certificate Authority Manager
Handles:
  - CA initialization (self-signed root certificate)
  - Authentication certificate generation and signing (for TLS/HTTPS)
  - Signature certificate generation and signing (for message signing)
  - Certificate chain management
  - Proper X.509 v3 extensions and standards
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
import logging

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class CertificateAuthority:
    """
    Complete Public Key Infrastructure Certificate Authority
    Generates and manages:
    - Root CA certificate (self-signed)
    - Authentication certificates (for TLS/HTTPS)
    - Signature certificates (for message signing)
    """

    def __init__(self, ca_dir: str = "CA_management/pki", config: dict = None):
        """
        Initialize CA with directory structure and configuration
        
        Args:
            ca_dir: Directory to store CA keys and certificates
            config: Configuration dict with server details
        """
        self.ca_dir = Path(ca_dir)
        self.ca_dir.mkdir(exist_ok=True, parents=True)
        
        self.keys_dir = self.ca_dir / "keys"
        self.certs_dir = self.ca_dir / "certs"
        self.certs_dir.mkdir(exist_ok=True)
        self.keys_dir.mkdir(exist_ok=True)
        
        self.config = config or {}
        self.ca_key_path = self.keys_dir / "ca_private_key.pem"
        self.ca_cert_path = self.certs_dir / "ca_root.crt"
        
        logger.info(f"[CA-AUTH] Initialized Certificate Authority directory: {self.ca_dir}")
        
        # Initialize CA if not exists
        if not self.ca_cert_path.exists():
            self._initialize_root_ca()
        else:
            logger.info("[CA-AUTH] Root CA certificate already exists")

    def _initialize_root_ca(self):
        """Generate self-signed root CA certificate"""
        logger.info("[CA-AUTH] Initializing root CA certificate...")
        
        # Generate CA private key
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        # Save CA private key
        with open(self.ca_key_path, "wb") as f:
            f.write(ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        logger.info(f"[CA-AUTH] CA private key saved: {self.ca_key_path}")
        
        # Create CA certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "EE"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Harjumaa"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Tallinn"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Trust Authority"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Root Certification Authority"),
        ])
        
        ca_cert = x509.CertificateBuilder().add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        ).subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)  # 10 years
        ).sign(ca_key, hashes.SHA256(), default_backend())
        
        # Save CA certificate
        with open(self.ca_cert_path, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        logger.info(f"[CA-AUTH] ✅ Root CA certificate created: {self.ca_cert_path}")

    def _load_ca_key(self):
        """Load CA private key"""
        with open(self.ca_key_path, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )

    def _load_ca_cert(self):
        """Load CA certificate"""
        with open(self.ca_cert_path, "rb") as f:
            return x509.load_pem_x509_certificate(
                f.read(),
                default_backend()
            )

    def generate_auth_certificate(self, server_id: str, server_name: str, 
                                 address: str, organization: str, 
                                 public_key_pem: str) -> tuple:
        """
        Generate Authentication certificate (for TLS/HTTPS) signed by CA
        
        Args:
            server_id: Security Server ID
            server_name: Security Server name
            address: Server IP/hostname
            organization: Organization name
            public_key_pem: Public key in PEM format
            
        Returns:
            (certificate_pem, certificate_path): Signed certificate and its path
        """
        logger.info(f"[CA-AUTH] Generating Authentication certificate for {server_id}")
        
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode() if isinstance(public_key_pem, str) else public_key_pem,
                backend=default_backend()
            )
            
            # Load CA key and cert
            ca_key = self._load_ca_key()
            ca_cert = self._load_ca_cert()
            
            # Create subject for Authentication certificate
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "EE"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Harjumaa"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Tallinn"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, f"AUTH-{server_id}"),
            ])
            
            # Build certificate with proper extensions
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(ca_cert.subject)
            builder = builder.public_key(public_key)
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.utcnow())
            builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=365))
            
            # Add extensions
            builder = builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=True,
            )
            
            # Subject Alternative Name (for hostname/IP)
            builder = builder.add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(address),
                    x509.DNSName(server_name),
                ]),
                critical=False,
            )
            
            # Subject Key Identifier
            builder = builder.add_extension(
                x509.SubjectKeyIdentifier.from_public_key(public_key),
                critical=False,
            )
            
            # Authority Key Identifier
            builder = builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                critical=False,
            )
            
            # Sign certificate
            auth_cert = builder.sign(ca_key, hashes.SHA256(), default_backend())
            
            # Save certificate
            cert_filename = f"auth_{server_id}_{datetime.utcnow().timestamp()}.crt"
            cert_path = self.certs_dir / cert_filename
            
            cert_pem = auth_cert.public_bytes(serialization.Encoding.PEM)
            with open(cert_path, "wb") as f:
                f.write(cert_pem)
            
            logger.info(f"[CA-AUTH] ✅ Authentication certificate generated: {cert_path}")
            return cert_pem.decode(), str(cert_path)
            
        except Exception as e:
            logger.error(f"[CA-AUTH] Error generating Authentication certificate: {e}")
            raise

    def generate_sign_certificate(self, server_id: str, server_name: str,
                                 organization: str, public_key_pem: str) -> tuple:
        """
        Generate Signature certificate (for message signing) signed by CA
        
        Args:
            server_id: Security Server ID
            server_name: Security Server name
            organization: Organization name
            public_key_pem: Public key in PEM format
            
        Returns:
            (certificate_pem, certificate_path): Signed certificate and its path
        """
        logger.info(f"[CA-AUTH] Generating Signature certificate for {server_id}")
        
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode() if isinstance(public_key_pem, str) else public_key_pem,
                backend=default_backend()
            )
            
            # Load CA key and cert
            ca_key = self._load_ca_key()
            ca_cert = self._load_ca_cert()
            
            # Create subject for Signature certificate
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "EE"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Harjumaa"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Tallinn"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, f"SIGN-{server_id}"),
            ])
            
            # Build certificate
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(ca_cert.subject)
            builder = builder.public_key(public_key)
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.utcnow())
            builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=365))
            
            # Add extensions
            builder = builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=True,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            
            # Extended Key Usage
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CODE_SIGNING]),
                critical=True,
            )
            
            # Subject Key Identifier
            builder = builder.add_extension(
                x509.SubjectKeyIdentifier.from_public_key(public_key),
                critical=False,
            )
            
            # Authority Key Identifier
            builder = builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                critical=False,
            )
            
            # Sign certificate
            sign_cert = builder.sign(ca_key, hashes.SHA256(), default_backend())
            
            # Save certificate
            cert_filename = f"sign_{server_id}_{datetime.utcnow().timestamp()}.crt"
            cert_path = self.certs_dir / cert_filename
            
            cert_pem = sign_cert.public_bytes(serialization.Encoding.PEM)
            with open(cert_path, "wb") as f:
                f.write(cert_pem)
            
            logger.info(f"[CA-AUTH] ✅ Signature certificate generated: {cert_path}")
            return cert_pem.decode(), str(cert_path)
            
        except Exception as e:
            logger.error(f"[CA-AUTH] Error generating Signature certificate: {e}")
            raise

    def get_ca_certificate(self) -> str:
        """Return CA root certificate in PEM format"""
        with open(self.ca_cert_path, "rb") as f:
            return f.read().decode()

    def get_certificate_chain(self, server_id: str) -> dict:
        """
        Get complete certificate chain for a server
        
        Returns:
            dict with root_ca, auth_cert, sign_cert paths
        """
        logger.info(f"[CA-AUTH] Retrieved certificate chain for {server_id}")
        
        # Find latest Authentication and Signature certificates
        auth_certs = list(self.certs_dir.glob(f"auth_{server_id}_*.crt"))
        sign_certs = list(self.certs_dir.glob(f"sign_{server_id}_*.crt"))
        
        return {
            "root_ca": str(self.ca_cert_path),
            "auth_cert": str(auth_certs[-1]) if auth_certs else None,
            "sign_cert": str(sign_certs[-1]) if sign_certs else None,
            "timestamp": datetime.utcnow().isoformat()
        }

    def sign_csr(self, csr_pem: str, server_id: str, cert_type: str = "auth") -> tuple:
        """
        Sign a Certificate Signing Request (CSR) and return signed certificate
        
        Args:
            csr_pem: CSR in PEM format
            server_id: Security Server ID (used in certificate subject)
            cert_type: "auth" for TLS or "sign" for message signing
            
        Returns:
            (certificate_pem, certificate_path): Signed certificate and its path
        """
        # Sanitize server_id to remove whitespace and invalid filename characters
        server_id = server_id.strip().replace('\t', '').replace('\n', '').replace('\r', '')
        server_id = ''.join(c if c.isalnum() or c in ['_', '-', '.'] else '_' for c in server_id)
        
        logger.info(f"[CA-AUTH] Signing CSR for {server_id} (type: {cert_type})")
        
        try:
            # Validate and clean CSR PEM format
            if isinstance(csr_pem, str):
                csr_pem = csr_pem.strip()
            else:
                csr_pem = csr_pem.decode().strip()
            
            # Check for proper PEM markers
            if not csr_pem.startswith("-----BEGIN CERTIFICATE REQUEST-----"):
                raise ValueError("CSR must start with '-----BEGIN CERTIFICATE REQUEST-----'")
            if not csr_pem.endswith("-----END CERTIFICATE REQUEST-----"):
                raise ValueError("CSR must end with '-----END CERTIFICATE REQUEST-----'")
            
            logger.info(f"[CA-AUTH] CSR format validated. Length: {len(csr_pem)} chars")
            
            # Parse CSR
            try:
                csr = x509.load_pem_x509_csr(
                    csr_pem.encode(),
                    default_backend()
                )
            except Exception as parse_error:
                logger.error(f"[CA-AUTH] CSR parsing error: {parse_error}")
                raise ValueError(f"Invalid CSR format: {str(parse_error)}")
            
            logger.info(f"[CA-AUTH] CSR parsed successfully. Subject: {csr.subject}")
            
            # Extract public key from CSR
            public_key = csr.public_key()
            
            # Load CA key and cert
            ca_key = self._load_ca_key()
            ca_cert = self._load_ca_cert()
            
            # Get subject from CSR but update CN if needed
            subject = csr.subject
            
            # Build certificate
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(ca_cert.subject)
            builder = builder.public_key(public_key)
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.utcnow())
            builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=365))
            
            # Add extensions based on certificate type
            builder = builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            
            if cert_type.lower() == "auth":
                # Authentication certificate extensions (TLS/HTTPS)
                builder = builder.add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        content_commitment=False,
                        key_encipherment=True,
                        data_encipherment=False,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                builder = builder.add_extension(
                    x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
                    critical=True,
                )
            else:
                # Signature certificate extensions (message signing)
                builder = builder.add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        content_commitment=True,
                        key_encipherment=False,
                        data_encipherment=False,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                builder = builder.add_extension(
                    x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CODE_SIGNING]),
                    critical=True,
                )
            
            # Subject Key Identifier
            builder = builder.add_extension(
                x509.SubjectKeyIdentifier.from_public_key(public_key),
                critical=False,
            )
            
            # Authority Key Identifier
            builder = builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                critical=False,
            )
            
            # Sign certificate
            signed_cert = builder.sign(ca_key, hashes.SHA256(), default_backend())
            
            # Save certificate
            cert_type_clean = cert_type.strip().upper()
            cert_filename = f"{cert_type_clean}_{server_id}_{datetime.utcnow().timestamp()}.crt"
            cert_path = self.certs_dir / cert_filename
            
            cert_pem = signed_cert.public_bytes(serialization.Encoding.PEM)
            with open(cert_path, "wb") as f:
                f.write(cert_pem)
            
            logger.info(f"[CA-AUTH] ✅ CSR signed successfully: {cert_path}")
            return cert_pem.decode(), str(cert_path)
            
        except Exception as e:
            logger.error(f"[CA-AUTH] Error signing CSR: {e}")
            raise

    def export_certificate_bundle(self, server_id: str, output_path: str = None) -> str:
        """
        Export complete certificate bundle (root CA + auth + sign)
        
        Args:
            server_id: Security Server ID
            output_path: Path to save bundle (optional)
            
        Returns:
            Path to bundle file
        """
        logger.info(f"[CA-AUTH] Exporting certificate bundle for {server_id}")
        
        bundle_path = output_path or self.ca_dir / f"bundle_{server_id}.pem"
        
        with open(bundle_path, "w") as bundle:
            # Add CA root
            with open(self.ca_cert_path, "r") as ca:
                bundle.write(ca.read())
                bundle.write("\n")
            
            # Add Authentication cert
            auth_certs = list(self.certs_dir.glob(f"auth_{server_id}_*.crt"))
            if auth_certs:
                with open(auth_certs[-1], "r") as auth:
                    bundle.write(auth.read())
                    bundle.write("\n")
            
            # Add Signature cert
            sign_certs = list(self.certs_dir.glob(f"sign_{server_id}_*.crt"))
            if sign_certs:
                with open(sign_certs[-1], "r") as sign:
                    bundle.write(sign.read())
                    bundle.write("\n")
        
        logger.info(f"[CA-AUTH] ✅ Certificate bundle exported: {bundle_path}")
        return str(bundle_path)


# Global CA instance
_ca_instance = None


def get_certificate_authority(config: dict = None) -> CertificateAuthority:
    """Get or create global Certificate Authority instance"""
    global _ca_instance
    if _ca_instance is None:
        _ca_instance = CertificateAuthority(config=config)
    return _ca_instance
