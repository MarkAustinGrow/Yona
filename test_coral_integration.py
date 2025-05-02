#!/usr/bin/env python
"""
Test script for Coral integration with YonaAgent.

This script tests the basic functionality of the Coral integration,
including connecting to the Coral server, registering the agent,
and sending/receiving messages.
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coral_adapter import YonaAgentWithCoral, start_coral_background

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("coral_integration_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_coral_connection(coral_server_url):
    """
    Test connecting to the Coral server.
    
    Args:
        coral_server_url: URL of the Coral server
    """
    logger.info(f"Testing connection to Coral server at: {coral_server_url}")
    
    # Initialize YonaAgentWithCoral
    agent = YonaAgentWithCoral(coral_server_url=coral_server_url)
    
    # Initialize Coral connection
    await agent.initialize_coral()
    
    logger.info("Coral connection initialized")
    
    # Wait for a moment to ensure connection is established
    await asyncio.sleep(5)
    
    return agent

async def test_create_thread(agent, collaborator_ids):
    """
    Test creating a thread with collaborators.
    
    Args:
        agent: YonaAgentWithCoral instance
        collaborator_ids: List of collaborator agent IDs
    """
    logger.info(f"Testing thread creation with collaborators: {collaborator_ids}")
    
    # Create a thread
    thread_id = await agent.create_collaboration(collaborator_ids)
    
    if thread_id:
        logger.info(f"Successfully created thread: {thread_id}")
    else:
        logger.error("Failed to create thread")
    
    return thread_id

async def test_send_message(agent, thread_id, message, mentions):
    """
    Test sending a message to a thread.
    
    Args:
        agent: YonaAgentWithCoral instance
        thread_id: Thread ID to send the message to
        message: Message content
        mentions: List of agent IDs to mention
    """
    logger.info(f"Testing sending message to thread {thread_id}")
    
    # Send a message
    result = await agent.coral.send_message(thread_id, message, mentions)
    
    if result:
        logger.info(f"Successfully sent message: {result}")
    else:
        logger.error("Failed to send message")
    
    return result

async def main():
    """Run the Coral integration tests."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get Coral server URL from environment or use default
        coral_server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:3001")
        
        # Test Coral connection
        agent = await test_coral_connection(coral_server_url)
        
        # Define collaborator IDs (replace with actual agent IDs)
        collaborator_ids = ["agent1", "agent2"]
        
        # Test thread creation
        thread_id = await test_create_thread(agent, collaborator_ids)
        
        if thread_id:
            # Test sending a message
            message = "Hello from Yona! This is a test message."
            await test_send_message(agent, thread_id, message, collaborator_ids)
            
            # Wait for a while to receive any responses
            logger.info("Waiting for responses...")
            await asyncio.sleep(30)
        
        logger.info("Tests completed")
    
    except Exception as e:
        logger.error(f"Error in Coral integration tests: {str(e)}")
        logger.exception("Exception details:")
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Tests stopped by user")
        print("Tests stopped")
