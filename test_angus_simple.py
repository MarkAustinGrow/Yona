#!/usr/bin/env python
"""
Simple test script for communicating with agent Angus using SimpleCoralAgent.
"""
import time
import uuid
import logging
from simple_coral_agent import SimpleCoralAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("angus_simple_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run the simple Angus communication test."""
    try:
        # Create a unique agent ID
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        logger.info(f"Created test agent with ID: {agent_id}")
        
        # Initialize the agent
        coral_server_url = "http://coral.pushcollective.club:3001"
        agent = SimpleCoralAgent(coral_server_url, agent_id)
        logger.info(f"Initialized SimpleCoralAgent with server URL: {coral_server_url}")
        
        # Connect to the Coral server
        logger.info("Connecting to Coral server...")
        if agent.connect():
            logger.info(f"Successfully connected agent {agent_id} to Coral server")
            
            # Register the agent
            logger.info("Registering agent...")
            if agent.register_agent(f"Test Agent {agent_id}", "A simple test agent for communicating with Angus"):
                logger.info(f"Successfully registered agent {agent_id}")
                
                # Create a thread with Angus
                angus_id = "did:web:angus.ai"
                logger.info(f"Creating thread with Angus (ID: {angus_id})...")
                thread_id = agent.create_thread([angus_id, agent_id])
                
                if thread_id:
                    logger.info(f"Created thread {thread_id} with Angus")
                    
                    # Send a message to Angus
                    message = "Hello Angus! This is a test message from a simple agent. Can you hear me?"
                    logger.info(f"Sending message to Angus: {message}")
                    
                    if agent.send_message(thread_id, message, mentions=[angus_id]):
                        logger.info("Successfully sent message to Angus")
                        
                        # Process any responses
                        logger.info("Waiting for responses...")
                        agent.process_messages(timeout=30)
                        
                        # Keep the agent running to receive messages
                        logger.info("Continuing to listen for messages...")
                        try:
                            while True:
                                agent.process_messages(timeout=5)
                                time.sleep(1)
                        except KeyboardInterrupt:
                            logger.info("Shutting down agent...")
                            agent.running = False
                    else:
                        logger.error("Failed to send message to Angus")
                else:
                    logger.error("Failed to create thread with Angus")
            else:
                logger.error("Failed to register agent")
        else:
            logger.error("Failed to connect to Coral server")
    
    except Exception as e:
        logger.error(f"Error in Angus communication test: {str(e)}")
        logger.exception("Exception details:")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
