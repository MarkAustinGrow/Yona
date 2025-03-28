#!/usr/bin/env python
"""
Run the Yona API server.

This script starts the Yona API server, which serves the capability document
and DID document for the Yona agent.
"""
import os
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the Yona API server."""
    parser = argparse.ArgumentParser(description='Run the Yona API server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--did-domain', default='yona.ai', help='Domain for the did:web identifier')
    parser.add_argument('--private-key', help='Path to a file containing a private key')
    args = parser.parse_args()
    
    try:
        # Check if Flask is installed
        try:
            from flask import Flask
        except ImportError:
            logger.error("Flask is not installed. Please install it with 'pip install flask'")
            return 1
        
        # Check if cryptography is installed
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519
        except ImportError:
            logger.error("Cryptography package is not installed. Please install it with 'pip install cryptography'")
            return 1
        
        # Import the API
        from src.api.endpoints import YonaAPI
        
        # Create and run the API
        api = YonaAPI(
            did_domain=args.did_domain,
            private_key_path=args.private_key
        )
        
        print(f"\nYona API server is running at http://{args.host}:{args.port}")
        print(f"DID: {api.did_manager.did}")
        print("\nAvailable endpoints:")
        print(f"  - Capability document: http://{args.host}:{args.port}/capabilities")
        print(f"  - DID document: http://{args.host}:{args.port}/.well-known/did.json")
        print(f"  - Health check: http://{args.host}:{args.port}/health")
        print("\nPress Ctrl+C to stop the server\n")
        
        api.run(host=args.host, port=args.port, debug=args.debug)
        
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error running API server: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
