#!/usr/bin/env python
"""
Yona Agent with Coral Protocol Integration

This script runs the Yona music agent with Coral Protocol integration,
allowing it to communicate with other agents through the Coral server.
"""

import os
import sys
import time
import logging
import argparse
from typing import Dict, Any, Optional

from src.agent import YonaAgent
from src.coral_adapter import YonaCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("yona_coral.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("yona_coral")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Run Yona agent with Coral Protocol integration')
    parser.add_argument('--server', default='coral.pushcollective.club', help='Coral server hostname')
    parser.add_argument('--http', action='store_true', help='Use HTTP instead of HTTPS')
    parser.add_argument('--app', default='default-app', help='Application ID')
    parser.add_argument('--key', default='public', help='Privacy key')
    parser.add_argument('--session', default=os.environ.get('YONA_SESSION_ID', 'yona-agent'), help='Session ID')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout for waiting for mentions (seconds)')
    parser.add_argument('--continuous', action='store_true', help='Run in continuous mode')
    parser.add_argument('--devmode', action='store_true', help='Use DevMode endpoints', default=True)
    parser.add_argument('--openai-key', help='OpenAI API key (defaults to environment variable)')
    args = parser.parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("coral_client").setLevel(logging.DEBUG)
        logging.getLogger("src.agent").setLevel(logging.DEBUG)
        logging.getLogger("src.coral_adapter").setLevel(logging.DEBUG)
    
    # Determine protocol
    protocol = "http" if args.http else "https"
    
    try:
        # Initialize Yona agent
        logger.info("Initializing Yona agent")
        yona = YonaAgent(openai_api_key=args.openai_key)
        
        # Create a Coral adapter
        logger.info(f"Creating Coral adapter with session ID: {args.session}")
        coral_adapter = YonaCoralAdapter(
            yona_agent=yona,
            session_id=args.session,
            app_id=args.app,
            privacy_key=args.key,
            server_url=f"{protocol}://{args.server}",
            use_devmode=args.devmode
        )
        
        # Register Yona with the Coral server
        agent_id = coral_adapter.register_agent()
        logger.info(f"Yona registered with Coral. Agent ID: {agent_id}")
        
        if not agent_id:
            logger.error("Failed to register Yona with Coral server. Exiting.")
            return 1
        
        if args.continuous:
            # Run in continuous mode
            logger.info("Starting continuous mode")
            success = coral_adapter.run_continuous()
            
            if not success:
                logger.error("Failed to run in continuous mode")
                return 1
            
            logger.info("Yona is now running in continuous mode. Press Ctrl+C to exit.")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                
        else:
            # Run in polling mode
            logger.info(f"Running in polling mode with timeout: {args.timeout} seconds")
            
            try:
                coral_adapter.run_polling(timeout_seconds=args.timeout)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
