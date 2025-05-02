#!/usr/bin/env python
"""
Run YonaAgent with Coral integration.

This script starts the YonaAgent with Coral integration enabled,
allowing it to communicate with other agents through the Coral server.
"""
import os
import sys
import time
import argparse
import logging
import threading
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coral_adapter import YonaAgentWithCoral, start_coral_background
from src.api.endpoints import YonaAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("yona_coral.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_api_server(host, port, debug, coral_agent):
    """
    Run the API server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Whether to run in debug mode
        coral_agent: YonaAgentWithCoral instance
    """
    # Create a custom YonaAPI that uses the coral_agent
    class YonaCoralAPI(YonaAPI):
        def __init__(self, coral_agent, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.coral_agent = coral_agent
            
            # Register additional routes
            self.app.route('/api/collaborations')(self.create_collaboration)
            
        def create_collaboration(self):
            """Create a collaboration thread with other agents."""
            from flask import request, jsonify
            
            data = request.json
            collaborator_ids = data.get('collaborator_ids', [])
            metadata = data.get('metadata', {})
            
            # Run the async function in a new event loop
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                thread_id = loop.run_until_complete(
                    self.coral_agent.create_collaboration(collaborator_ids, metadata)
                )
                return thread_id
            
            # Run the async function and get the result
            thread_id = run_async()
            
            if thread_id:
                return jsonify({"success": True, "thread_id": thread_id})
            else:
                return jsonify({"success": False, "error": "Failed to create collaboration"}), 500
    
    # Create the API with the coral_agent
    api = YonaCoralAPI(
        coral_agent=coral_agent,
        did_domain="yona.ai",
        private_key_path=None
    )
    
    logger.info(f"Starting API server on {host}:{port}")
    api.run(host=host, port=port, debug=debug)

def main():
    """Run YonaAgent with Coral integration."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Run YonaAgent with Coral integration')
        parser.add_argument('--host', default='127.0.0.1', help='Host to bind API server to')
        parser.add_argument('--port', type=int, default=5000, help='Port to bind API server to')
        parser.add_argument('--debug', action='store_true', help='Run in debug mode')
        parser.add_argument('--coral-server', default='http://coral.pushcollective.club:3001', 
                           help='URL of the Coral server')
        args = parser.parse_args()
        
        # Load environment variables
        load_dotenv()
        
        # Initialize YonaAgentWithCoral
        logger.info(f"Initializing YonaAgentWithCoral with Coral server: {args.coral_server}")
        coral_agent = YonaAgentWithCoral(coral_server_url=args.coral_server)
        
        # Start Coral background thread
        logger.info("Starting Coral background thread")
        coral_thread = start_coral_background(coral_agent)
        
        # Run the API server
        logger.info("Starting API server")
        run_api_server(args.host, args.port, args.debug, coral_agent)
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    
    except Exception as e:
        logger.error(f"Error running YonaAgent with Coral: {str(e)}")
        logger.exception("Exception details:")
        return 1

if __name__ == "__main__":
    sys.exit(main())
