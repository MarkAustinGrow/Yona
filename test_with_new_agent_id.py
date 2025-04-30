#!/usr/bin/env python3
"""
Test script for Coral Protocol integration with the new agent ID.
This script sends a message to the Yona agent with the updated agent ID.
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
logger = logging.getLogger("test_with_new_agent_id")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test Coral Protocol integration with new agent ID")
    parser.add_argument("--yona-agent-id", default="yona-agent", help="Yona agent ID")
    parser.add_argument("--youtube-agent-id", default="youtube-agent", help="YouTube agent ID")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--wait-time", type=int, default=60, help="Time to wait after sending message (seconds)")
    parser.add_argument("--session-id", default=f"test-session-{int(time.time())}", help="Session ID for the test")
    return parser.parse_args()

def main():
    """Main function to run the test."""
    args = parse_args()
    
    logger.info("Starting test with new agent ID")
    logger.info(f"Yona Agent ID: {args.yona_agent_id}")
    
    # Create Coral client
    client = CoralClient(
        session_id=args.session_id,
        server_url=args.server_url,
        use_devmode=True
    )
    
    # Create a thread with both agents
    logger.info(f"Creating thread with agents: {args.yona_agent_id} and {args.youtube_agent_id}")
    try:
        thread_id = client.create_thread([args.yona_agent_id, args.youtube_agent_id])
        logger.info(f"Thread created with ID: {thread_id}")
    except Exception as e:
        logger.error(f"Failed to create thread: {str(e)}")
        return
    
    # Send a message from YouTube agent to Yona with multiple mention formats
    logger.info(f"Sending message from {args.youtube_agent_id} to {args.yona_agent_id}")
    message_content = (
        f"@{args.yona_agent_id} Hey Yona, can you create a song about debugging? "
        f"Also trying alternate mention format: <@{args.yona_agent_id}> "
        "I'd like a fun, upbeat song about fixing bugs and making things work. "
        "This is a test message with the new agent ID."
    )
    
    try:
        message_id = client.send_message(
            thread_id=thread_id,
            content=message_content,
            mentions=[args.yona_agent_id]
        )
        logger.info(f"Message sent with ID: {message_id}")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return
    
    # Wait for a while to see if Yona responds
    logger.info(f"Waiting for {args.wait_time} seconds to see if Yona responds...")
    logger.info("Check the Yona logs in another terminal with: docker logs -f yona_yona-coral_1")
    
    try:
        # Keep the script running to monitor for responses
        for i in range(args.wait_time):
            time.sleep(1)
            if i % 10 == 0:
                logger.info(f"Still waiting... {i}/{args.wait_time} seconds elapsed")
    except KeyboardInterrupt:
        logger.info("Test interrupted")
    
    logger.info("Test completed")
    logger.info("If Yona didn't respond, check the following:")
    logger.info("1. Verify the agent ID is correct")
    logger.info("2. Check if the fix_coral_adapter.py script was run")
    logger.info("3. Examine the Yona logs for any errors in message processing")

if __name__ == "__main__":
    main()
