"""
DID Manager for Yona MCP implementation.

This module provides functionality for generating and managing
decentralized identities (DIDs) for the Yona agent.
"""
import os
import json
import uuid
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Try to import cryptography for key generation and signing
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    logger.warning("Cryptography package not available. Using simulated keys.")
    CRYPTO_AVAILABLE = False

class DIDManager:
    """
    Manager for decentralized identities (DIDs) for the Yona agent.
    
    This class provides functionality for:
    - Generating and managing DIDs
    - Creating DID documents
    - Signing requests with the DID's private key
    - Verifying signatures from other DIDs
    """
    
    def __init__(self, did_domain: str = "yona.ai", private_key_path: Optional[str] = None):
        """
        Initialize the DID Manager.
        
        Args:
            did_domain: Domain for the did:web identifier
            private_key_path: Path to a file containing a private key
        """
        self.did_domain = did_domain
        self.did = f"did:web:{did_domain}"
        self.did_document = None
        self.private_key = None
        self.public_key = None
        
        # Check if cryptography is available
        if not CRYPTO_AVAILABLE:
            logger.error("Cryptography package is required but not available")
            raise ImportError("Cryptography package is required for DID operations")
        
        # Generate or load keys
        if private_key_path and os.path.exists(private_key_path):
            self._load_private_key(private_key_path)
        else:
            self._generate_keys()
            
        # Create DID document
        self._create_did_document()
        
        logger.info(f"DID Manager initialized with DID: {self.did}")
    
    def _generate_keys(self) -> None:
        """Generate public-private key pair for the DID."""
        # Generate real Ed25519 keys
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Store the keys
        self.private_key = private_key
        self.public_key = public_key
        
        logger.info("Generated Ed25519 key pair")
    
    def _load_private_key(self, private_key_path: str) -> None:
        """
        Load a private key from a file.
        
        Args:
            private_key_path: Path to the private key file
        """
        try:
            with open(private_key_path, "rb") as key_file:
                private_key_data = key_file.read()
                
            # Load the private key
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_data)
            public_key = private_key.public_key()
            
            self.private_key = private_key
            self.public_key = public_key
            
            logger.info(f"Loaded private key from {private_key_path}")
        except Exception as e:
            logger.error(f"Error loading private key: {str(e)}")
            logger.info("Falling back to generating new keys")
            self._generate_keys()
    
    def _create_did_document(self) -> None:
        """Create a DID document for the agent."""
        # Get the public key in multibase format
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        public_key_multibase = f"z{base64.b64encode(public_key_bytes).decode('ascii')}"
        
        # Create the DID document
        self.did_document = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": self.did,
            "verificationMethod": [{
                "id": f"{self.did}#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": self.did,
                "publicKeyMultibase": public_key_multibase
            }],
            "authentication": [f"{self.did}#keys-1"],
            "service": [{
                "id": f"{self.did}#music-api",
                "type": "MusicGenerationService",
                "serviceEndpoint": f"https://{self.did_domain}/api/music"
            }]
        }
        
        logger.info(f"Created DID document for {self.did}")
    
    def get_did_document(self) -> Dict[str, Any]:
        """
        Get the DID document.
        
        Returns:
            The DID document as a dictionary
        """
        return self.did_document
    
    def sign_request(self, data: Dict[str, Any]) -> str:
        """
        Sign a request with the private key.
        
        Args:
            data: Data to sign
            
        Returns:
            Base64-encoded signature
        """
        
        try:
            # Convert data to JSON string
            data_str = json.dumps(data, sort_keys=True)
            
            # Sign the data
            signature = self.private_key.sign(data_str.encode('utf-8'))
            
            # Return base64-encoded signature
            return base64.b64encode(signature).decode('ascii')
        except Exception as e:
            logger.error(f"Error signing request: {str(e)}")
            return ""
    
    def verify_signature(self, data: Dict[str, Any], signature: str, did_document: Dict[str, Any]) -> bool:
        """
        Verify a signature from another agent.
        
        Args:
            data: Data that was signed
            signature: Base64-encoded signature
            did_document: DID document of the signer
            
        Returns:
            True if the signature is valid, False otherwise
        """
        
        try:
            # Extract the public key from the DID document
            verification_method = did_document.get("verificationMethod", [])
            if not verification_method:
                logger.error("No verification method found in DID document")
                return False
            
            public_key_multibase = verification_method[0].get("publicKeyMultibase")
            if not public_key_multibase or not public_key_multibase.startswith("z"):
                logger.error("Invalid public key format in DID document")
                return False
            
            # Decode the public key
            public_key_bytes = base64.b64decode(public_key_multibase[1:])
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            # Convert data to JSON string
            data_str = json.dumps(data, sort_keys=True)
            
            # Decode the signature
            signature_bytes = base64.b64decode(signature)
            
            # Verify the signature
            public_key.verify(signature_bytes, data_str.encode('utf-8'))
            
            return True
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False
    
    def save_private_key(self, path: str) -> bool:
        """
        Save the private key to a file.
        
        Args:
            path: Path to save the private key
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            # Serialize the private key
            private_key_bytes = self.private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Write to file
            with open(path, "wb") as key_file:
                key_file.write(private_key_bytes)
            
            logger.info(f"Saved private key to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving private key: {str(e)}")
            return False
    
    def get_auth_headers(self, request_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Get authentication headers for a request.
        
        Args:
            request_data: Optional data to include in the signature
            
        Returns:
            Dictionary with authentication headers
        """
        # Create a data object with timestamp if none provided
        if request_data is None:
            request_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "nonce": str(uuid.uuid4())
            }
        
        # Sign the request
        signature = self.sign_request(request_data)
        
        # Return headers
        return {
            "X-DID": self.did,
            "X-DID-Signature": signature,
            "X-DID-Signed-Data": json.dumps(request_data)
        }
