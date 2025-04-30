#!/usr/bin/env python3
"""
Simple test script for Coral Protocol integration.
This script creates a thread with both agents and sends a message from YouTube agent to Yona.
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
logger = logging.getLogger("simple_coral_test")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Simple test for Coral Protocol integration")
    parser.add_argument("--yona-agent-id", default="yona-agent", help="Yona agent ID")
    parser.add_argument("--youtube-agent-id", default="youtube-agent", help="YouTube agent ID")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--wait-time", type=int, default=30, help="Time to wait after sending message (seconds)")
    parser.add_argument("--session-id", default=f"simple-test-{int(time.time())}", help="Session ID for the test")
    return parser.parse_args()

def main():
    """Main function to run the test."""
    args = parse_args()
    
    logger.info("Starting simple Coral Protocol test")
    logger.info(f"Yona Agent ID: {args.yona_agent_id}")
    logger.info(f"YouTube Agent ID: {args.youtube_agent_id}")
    
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
    
    # Send a message from YouTube agent to Yona
    logger.info(f"Sending message from {args.youtube_agent_id} to {args.yona_agent_id}")
    message_content = (
        f"@{args.yona_agent_id} Can you create a song about AI collaboration? "
        "I'd like a catchy tune that explains how different AI systems can work together. "
        "The song should be upbeat and mention how combining different AI capabilities "
        "creates something greater than the sum of its parts."
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
    time.sleep(args.wait_time)
    
    logger.info("Test completed. Check the Yona logs to see if it received and processed the message.")
    logger.info("If Yona received the message, you should see entries like:")
    logger.info("  - 'Received message mention from [agent_id] in thread [thread_id]'")
    logger.info("  - 'Processing mention from [agent_id]'")
    logger.info("  - 'Sending message to thread: [thread_id]'")

if __name__ == "__main__":
    main()
