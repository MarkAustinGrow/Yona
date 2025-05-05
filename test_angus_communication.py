#!/usr/bin/env python
"""
Test script for communicating with agent Angus.
"""
import os
import sys
import asyncio
import logging
import json
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coral_adapter import YonaAgentWithCoral

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("angus_communication_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_angus_communication(coral_server_url):
    """
    Test communicating with agent Angus.
    
    Args:
        coral_server_url: URL of the Coral server
    """
    logger.info(f"Testing communication with Angus via Coral server at: {coral_server_url}")
    
    # Initialize YonaAgentWithCoral
    agent = YonaAgentWithCoral(coral_server_url=coral_server_url)
    
    # Initialize Coral connection
    await agent.initialize_coral()
    
    logger.info("Coral connection initialized")
    
    # Wait for a moment to ensure connection is established
    await asyncio.sleep(5)
    
    # Create a thread with Angus
    angus_id = "did:web:angus.ai"
    logger.info(f"Creating thread with Angus (ID: {angus_id})")
    
    thread_id = await agent.create_collaboration([angus_id])
    
    if thread_id:
        logger.info(f"Successfully created thread: {thread_id}")
        
        # Send a message to Angus
        message = "Hello Angus! This is Yona, the AI music creator. Can you hear me?"
        logger.info(f"Sending message to Angus: {message}")
        
        result = await agent.coral.send_message(
            thread_id, 
            message, 
            mentions=[angus_id]
        )
        
        logger.info(f"Message send result: {result}")
        
        # Wait for a response
        logger.info("Waiting for a response from Angus...")
        await asyncio.sleep(30)
        
        logger.info("Test completed")
    else:
        logger.error("Failed to create thread with Angus")

async def main():
    """Run the Angus communication test."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get Coral server URL from environment or use default
        coral_server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:3001")
        
        # Test communication with Angus
        await test_angus_communication(coral_server_url)
        
    except Exception as e:
        logger.error(f"Error in Angus communication test: {str(e)}")
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
