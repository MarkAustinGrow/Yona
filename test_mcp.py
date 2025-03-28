#!/usr/bin/env python
"""
Test script for the MCP implementation.

This script tests the DID manager and capability document generation
without needing to run the full API server.
"""
import os
import json
import logging
import argparse
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_did_manager():
    """Test the DID manager."""
    print("\n=== Testing DID Manager ===\n")
    
    try:
        from src.identity.did_manager import DIDManager
        
        # Create DID manager
        did_manager = DIDManager(
            did_domain="yona.test"
        )
        
        # Print DID
        print(f"DID: {did_manager.did}")
        
        # Print DID document
        print("\nDID Document:")
        pprint(did_manager.get_did_document())
        
        # Test signing
        test_data = {"test": "data", "timestamp": "2025-03-21T15:00:00Z"}
        signature = did_manager.sign_request(test_data)
        print(f"\nSignature for test data: {signature}")
        
        # Test verification
        verification = did_manager.verify_signature(
            test_data, 
            signature, 
            did_manager.get_did_document()
        )
        print(f"Signature verification: {verification}")
        
        # Test auth headers
        print("\nAuth Headers:")
        pprint(did_manager.get_auth_headers())
        
        return True
    except Exception as e:
        logger.error(f"Error testing DID manager: {str(e)}")
        return False

def test_capability_document():
    """Test the capability document generation."""
    print("\n=== Testing Capability Document ===\n")
    
    try:
        from src.protocol.capability_document import CapabilityDocument
        
        # Create capability document generator
        capability_generator = CapabilityDocument(
            did="did:web:yona.test",
            agent_name="Yona Test",
            agent_description="Test instance of Yona AI"
        )
        
        # Print capability document
        print("Capability Document:")
        pprint(capability_generator.generate())
        
        # Test adding a custom service
        capability_generator.add_service(
            service_id="test-service",
            service_type="TestService",
            description="A test service",
            input_schema={"test": "string"},
            output_schema={"result": "string"}
        )
        
        # Print updated capability document
        print("\nUpdated Capability Document (with custom service):")
        pprint(capability_generator.generate())
        
        return True
    except Exception as e:
        logger.error(f"Error testing capability document: {str(e)}")
        return False

def main():
    """Run the tests."""
    # Check if cryptography is installed
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError:
        logger.error("Cryptography package is not installed. Please install it with 'pip install cryptography'")
        return 1
    
    # Run tests
    did_success = test_did_manager()
    capability_success = test_capability_document()
    
    # Print summary
    print("\n=== Test Summary ===\n")
    print(f"DID Manager: {'SUCCESS' if did_success else 'FAILED'}")
    print(f"Capability Document: {'SUCCESS' if capability_success else 'FAILED'}")
    
    return 0 if did_success and capability_success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
