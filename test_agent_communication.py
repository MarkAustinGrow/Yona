#!/usr/bin/env python3
"""
Test script to verify communication between Yona and YouTube agents via Coral Protocol.
This script creates a thread with both agents and has the YouTube agent request a song from Yona.
"""

import logging
import time
import argparse
from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_communication_test")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test communication between Yona and YouTube agents")
    parser.add_argument("--yona-agent-id", default="yona-agent", help="Yona agent ID")
    parser.add_argument("--youtube-agent-id", default="youtube-agent", help="YouTube agent ID")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--wait-time", type=int, default=60, help="Time to wait for responses (seconds)")
    parser.add_argument("--session-id", default=f"test-session-{int(time.time())}", help="Session ID for the test")
    return parser.parse_args()

def create_test_thread(client, yona_agent_id, youtube_agent_id):
    """Create a thread with both agents."""
    logger.info(f"Creating thread with agents: {yona_agent_id} and {youtube_agent_id}")
    
    try:
        thread_id = client.create_thread([yona_agent_id, youtube_agent_id])
        logger.info(f"Created thread with ID: {thread_id}")
        return thread_id
    except Exception as e:
        logger.error(f"Failed to create thread: {str(e)}")
        return None

def send_test_message(client, thread_id, youtube_agent_id, yona_agent_id):
    """Send a test message from YouTube agent to Yona agent."""
    logger.info(f"Sending test message from {youtube_agent_id} to {yona_agent_id}")
    
    message_content = (
        f"@{yona_agent_id} Please create a song about AI collaboration. "
        "I'd like to analyze it and upload it to YouTube. "
        "The song should be upbeat and mention how different AI systems can work together."
    )
    
    try:
        message_id = client.send_message(
            thread_id=thread_id,
            content=message_content,
            mentions=[yona_agent_id]
        )
        logger.info(f"Sent message with ID: {message_id}")
        return message_id
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return None

def check_for_responses(client, thread_id, wait_time):
    """Check for responses in the thread."""
    logger.info(f"Waiting {wait_time} seconds for responses...")
    
    # Wait for responses
    time.sleep(wait_time)
    
    try:
        # Get messages in the thread
        messages = client.get_thread_messages(thread_id)
        
        if not messages:
            logger.warning("No messages found in the thread")
            return False
        
        logger.info(f"Found {len(messages)} messages in the thread")
        
        # Print messages
        for i, msg in enumerate(messages):
            sender = msg.get('sender_id', 'Unknown')
            content = msg.get('content', 'No content')
            logger.info(f"Message {i+1} from {sender}: {content[:100]}...")
        
        # Check if there's more than one message (our initial message + responses)
        return len(messages) > 1
    except Exception as e:
        logger.error(f"Failed to get thread messages: {str(e)}")
        return False

def main():
    """Main function to run the test."""
    args = parse_args()
    
    logger.info("Starting agent communication test")
    logger.info(f"Yona Agent ID: {args.yona_agent_id}")
    logger.info(f"YouTube Agent ID: {args.youtube_agent_id}")
    
    # Create Coral client
    client = CoralClient(
        session_id=args.session_id,
        server_url=args.server_url,
        use_devmode=True
    )
    
    # Create thread
    thread_id = create_test_thread(client, args.yona_agent_id, args.youtube_agent_id)
    if not thread_id:
        logger.error("Test failed: Could not create thread")
        return
    
    # Send message
    message_id = send_test_message(client, thread_id, args.youtube_agent_id, args.yona_agent_id)
    if not message_id:
        logger.error("Test failed: Could not send message")
        return
    
    # Check for responses
    has_responses = check_for_responses(client, thread_id, args.wait_time)
    
    if has_responses:
        logger.info("Test PASSED: Communication between agents was successful")
    else:
        logger.warning("Test FAILED: No response received from Yona agent")
    
    logger.info("Test completed")

if __name__ == "__main__":
    main()
