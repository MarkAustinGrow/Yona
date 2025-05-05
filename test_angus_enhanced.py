#!/usr/bin/env python
"""
Enhanced test script for communicating with agent Angus.

This script extends the YonaAgentWithCoral class to add more detailed
logging of the communication with agent Angus.
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
        logging.FileHandler("angus_enhanced_test.log"),
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
    
    async def create_collaboration(self, collaborator_ids: List[str], metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Enhanced collaboration creation with detailed logging.
        
        Args:
            collaborator_ids: List of agent IDs to collaborate with
            metadata: Optional metadata for the thread
            
        Returns:
            Thread ID if successful, None otherwise
        """
        logger.info(f"DETAILED COLLABORATION: Creating thread with {collaborator_ids}")
        
        # Call the parent method to create the collaboration
        thread_id = await super().create_collaboration(collaborator_ids, metadata)
        
        if thread_id:
            logger.info(f"DETAILED COLLABORATION: Successfully created thread {thread_id}")
        else:
            logger.error("DETAILED COLLABORATION: Failed to create thread")
        
        return thread_id

async def test_angus_communication(coral_server_url):
    """
    Test communicating with agent Angus using the enhanced agent.
    
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
    
    # Create a thread with Angus
    angus_id = "did:web:angus.ai"
    logger.info(f"Creating thread with Angus (ID: {angus_id})")
    
    thread_id = await agent.create_collaboration([angus_id])
    
    if thread_id:
        logger.info(f"Successfully created thread: {thread_id}")
        
        # Send a message to Angus
        message = "Hello Angus! This is Yona, the AI music creator. Can you hear me?"
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
        logger.info("Waiting for a response from Angus...")
        
        # Wait longer to give Angus time to respond
        for i in range(6):
            logger.info(f"Still waiting... ({i+1}/6)")
            await asyncio.sleep(10)
        
        logger.info("Test completed")
    else:
        logger.error("Failed to create thread with Angus")

async def main():
    """Run the enhanced Angus communication test."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get Coral server URL from environment or use default
        coral_server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:3001")
        
        # Test communication with Angus
        await test_angus_communication(coral_server_url)
        
    except Exception as e:
        logger.error(f"Error in enhanced Angus communication test: {str(e)}")
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
