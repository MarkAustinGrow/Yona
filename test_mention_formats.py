#!/usr/bin/env python3
"""
Test script for Coral Protocol mention formats.

This script tests different mention formats to see which ones work with the Coral Protocol.
It sends messages with various mention formats and checks if they are detected.
"""

import logging
import time
import argparse
import sys
from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_mention_formats")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test Coral Protocol mention formats")
    parser.add_argument("--yona-agent-id", default="yona-agent", help="Yona agent ID")
    parser.add_argument("--youtube-agent-id", default="youtube-agent", help="YouTube agent ID")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--wait-time", type=int, default=10, help="Time to wait between messages (seconds)")
    parser.add_argument("--session-id", default=f"mention-test-{int(time.time())}", help="Session ID for the test")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def test_mention_formats(args):
    """Test different mention formats."""
    logger.info("Starting mention format test")
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
        return False
    
    # Test different mention formats
    mention_formats = [
        {
            "name": "Explicit mention in API call only",
            "content": "Can you create a song about testing?",
            "mentions": [args.yona_agent_id]
        },
        {
            "name": "@mention in content",
            "content": f"@{args.yona_agent_id} Can you create a song about debugging?",
            "mentions": []
        },
        {
            "name": "<@mention> in content",
            "content": f"<@{args.yona_agent_id}> Can you create a song about coding?",
            "mentions": []
        },
        {
            "name": "Name mention in content",
            "content": "Hey Yona, can you create a song about AI?",
            "mentions": []
        },
        {
            "name": "Combined mentions",
            "content": f"@{args.yona_agent_id} Hey Yona, can you create a song about music?",
            "mentions": [args.yona_agent_id]
        }
    ]
    
    for i, format_test in enumerate(mention_formats):
        logger.info(f"Testing mention format {i+1}/{len(mention_formats)}: {format_test['name']}")
        
        try:
            # Send message with this mention format
            message_id = client.send_message(
                thread_id=thread_id,
                content=format_test["content"],
                mentions=format_test["mentions"]
            )
            logger.info(f"Message sent with ID: {message_id}")
            
            # Wait for a response
            logger.info(f"Waiting {args.wait_time} seconds for a response...")
            time.sleep(args.wait_time)
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
    
    logger.info("Mention format test completed")
    logger.info("Check the Yona logs to see which mention formats were detected")
    logger.info("Command: docker logs yona_yona-coral_1 | grep 'Found mention'")
    
    return True

def main():
    """Main function."""
    args = parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("coral_client").setLevel(logging.DEBUG)
    
    success = test_mention_formats(args)
    
    if success:
        logger.info("Test completed successfully")
        return 0
    else:
        logger.error("Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
