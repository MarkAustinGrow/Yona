"""
API Endpoints for Yona MCP implementation.

This module provides API endpoints for serving the capability document
and handling requests to the Yona agent.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request, Response

from src.identity.did_manager import DIDManager
from src.protocol.capability_document import CapabilityDocument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YonaAPI:
    """
    API server for the Yona agent.
    
    This class provides functionality for:
    - Serving the capability document
    - Handling requests to the Yona agent
    - Authenticating requests using DIDs
    """
    
    def __init__(self, did_domain: str = "yona.ai", 
                 private_key_path: Optional[str] = None):
        """
        Initialize the Yona API.
        
        Args:
            did_domain: Domain for the did:web identifier
            private_key_path: Path to a file containing a private key
        """
        # Initialize DID manager
        self.did_manager = DIDManager(
            did_domain=did_domain,
            private_key_path=private_key_path
        )
        
        # Initialize capability document generator
        self.capability_generator = CapabilityDocument(
            did=self.did_manager.did,
            agent_name="Yona AI",
            agent_description="An AI K-pop star that creates songs based on prompts and feedback"
        )
        
        # Create Flask app
        self.app = Flask(__name__)
        
        # Register routes
        self._register_routes()
        
        logger.info(f"Yona API initialized with DID: {self.did_manager.did}")
    
    def _register_routes(self) -> None:
        """Register API routes."""
        # Capability document endpoint
        self.app.route('/capabilities')(self.get_capabilities)
        
        # DID document endpoint
        self.app.route('/.well-known/did.json')(self.get_did_document)
        
        # Health check endpoint
        self.app.route('/health')(self.health_check)
    
    def get_capabilities(self) -> Response:
        """
        Serve the capability document.
        
        Returns:
            JSON response with the capability document
        """
        logger.info("Serving capability document")
        return jsonify(self.capability_generator.generate())
    
    def get_did_document(self) -> Response:
        """
        Serve the DID document.
        
        Returns:
            JSON response with the DID document
        """
        logger.info("Serving DID document")
        return jsonify(self.did_manager.get_did_document())
    
    def health_check(self) -> Response:
        """
        Health check endpoint.
        
        Returns:
            JSON response with status information
        """
        return jsonify({
            "status": "ok",
            "did": self.did_manager.did,
            "version": "0.1.0"
        })
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> None:
        """
        Run the API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Whether to run in debug mode
        """
        logger.info(f"Starting Yona API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app(did_domain: str = "yona.ai", 
              private_key_path: Optional[str] = None) -> Flask:
    """
    Create a Flask application for the Yona API.
    
    Args:
        did_domain: Domain for the did:web identifier
        private_key_path: Path to a file containing a private key
        
    Returns:
        Flask application
    """
    api = YonaAPI(
        did_domain=did_domain,
        private_key_path=private_key_path
    )
    return api.app


if __name__ == '__main__':
    # If run directly, start the server
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the Yona API server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--did-domain', default='yona.ai', help='Domain for the did:web identifier')
    parser.add_argument('--private-key', help='Path to a file containing a private key')
    args = parser.parse_args()
    
    api = YonaAPI(
        did_domain=args.did_domain,
        private_key_path=args.private_key
    )
    
    api.run(host=args.host, port=args.port, debug=args.debug)
