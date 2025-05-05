#!/usr/bin/env python
"""
Test script for communicating with agent Angus using multiple possible agent IDs.

This script attempts to communicate with agent Angus using different possible
agent IDs to determine which one works.
"""
import os
import sys
import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coral_adapter import YonaAgentWithCoral

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("angus_multiple_ids_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedYonaAgent(YonaAgentWithCoral):
    """
    Enhanced version of YonaAgentWithCoral with improved logging.
    """
    
    async def handle_coral_message(self, message: Dict[str, Any]):
        """
        Enhanced message handler with detailed logging.
        
        Args:
            message: Message received from Coral
        """
        logger.info(f"DETAILED MESSAGE RECEIVED: {json.dumps(message, indent=2)}")
        
        # Call the parent method to handle the message normally
        await super().handle_coral_message(message)
    
    async def _handle_mention(self, message: Dict[str, Any]):
        """
        Enhanced mention handler with detailed logging.
        
        Args:
            message: Mention message
        """
        thread_id = message.get("thread_id")
        sender_id = message.get("sender_id")
        content = message.get("content", "")
        
        logger.info(f"DETAILED MENTION: From {sender_id} in thread {thread_id}: {content}")
        logger.info(f"Full mention structure: {json.dumps(message, indent=2)}")
        
        # Call the parent method to handle the mention normally
        await super()._handle_mention(message)

async def test_angus_id(agent, angus_id):
    """
    Test communication with a specific Angus ID.
    
    Args:
        agent: EnhancedYonaAgent instance
        angus_id: Agent ID to test
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Testing communication with Angus ID: {angus_id}")
    
    try:
        # Create a thread with Angus
        logger.info(f"Creating thread with Angus (ID: {angus_id})")
        thread_id = await agent.create_collaboration([angus_id])
        
        if not thread_id:
            logger.error(f"Failed to create thread with Angus ID: {angus_id}")
            return False
        
        logger.info(f"Successfully created thread: {thread_id}")
        
        # Send a message to Angus
        message = f"Hello Angus ({angus_id})! This is Yona, the AI music creator. Can you hear me?"
        logger.info(f"Sending message to Angus: {message}")
        
        # Add a signature if DID is available
        signature_info = None
        if agent.coral_did:
            signature_info = agent.coral_did.sign_message(message)
            logger.info("Signed message with DID")
        
        result = await agent.coral.send_message(
            thread_id, 
            message, 
            mentions=[angus_id],
            signature_info=signature_info
        )
        
        logger.info(f"Message send result: {result}")
        
        # Wait for a response
        logger.info(f"Waiting for a response from Angus ({angus_id})...")
        
        # Wait for a short time to see if we get a response
        await asyncio.sleep(10)
        
        logger.info(f"Test completed for Angus ID: {angus_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error testing Angus ID {angus_id}: {str(e)}")
        logger.exception("Exception details:")
        return False

async def test_multiple_angus_ids(coral_server_url):
    """
    Test communicating with agent Angus using multiple possible agent IDs.
    
    Args:
        coral_server_url: URL of the Coral server
    """
    logger.info(f"Testing communication with Angus via Coral server at: {coral_server_url}")
    
    # Initialize EnhancedYonaAgent
    agent = EnhancedYonaAgent(coral_server_url=coral_server_url)
    
    # Initialize Coral connection
    await agent.initialize_coral()
    
    logger.info("Coral connection initialized")
    
    # Wait for a moment to ensure connection is established
    await asyncio.sleep(5)
    
    # List of possible Angus IDs to try
    angus_ids = [
        "did:web:angus.ai",
        "angus",
        "agent_angus",
        "did:web:agent:angus",
        "angus_ai",
        "angus.ai"
    ]
    
    # Test each Angus ID
    results = {}
    for angus_id in angus_ids:
        success = await test_angus_id(agent, angus_id)
        results[angus_id] = "Success" if success else "Failed"
    
    # Log the results
    logger.info("Results of testing multiple Angus IDs:")
    for angus_id, result in results.items():
        logger.info(f"  {angus_id}: {result}")
    
    # Wait a bit longer to see if we get any responses
    logger.info("Waiting for any delayed responses...")
    await asyncio.sleep(30)
    
    logger.info("All tests completed")

async def main():
    """Run the multiple Angus IDs test."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get Coral server URL from environment or use default
        coral_server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:3001")
        
        # Test communication with Angus using multiple IDs
        await test_multiple_angus_ids(coral_server_url)
        
    except Exception as e:
        logger.error(f"Error in multiple Angus IDs test: {str(e)}")
        logger.exception("Exception details:")
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
        print("Test stopped")
