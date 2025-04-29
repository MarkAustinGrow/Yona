#!/usr/bin/env python3
"""
Auto Test Script for Coral Protocol Integration

This script automatically extracts the current Yona agent ID from Docker logs,
then creates a thread and sends test messages with the correct agent ID.
"""

import logging
import time
import argparse
import subprocess
import re
import sys
from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("auto_test_coral")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Auto Test Coral Protocol Integration")
    parser.add_argument("--youtube-agent-id", default="youtube-agent", help="YouTube agent ID")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--wait-time", type=int, default=60, help="Time to wait after sending message (seconds)")
    parser.add_argument("--session-id", default=f"auto-test-{int(time.time())}", help="Session ID for the test")
    parser.add_argument("--container-name", default="yona_yona-coral_1", help="Docker container name")
    parser.add_argument("--tail-lines", type=int, default=200, help="Number of log lines to check")
    parser.add_argument("--retry-count", type=int, default=3, help="Number of times to retry if agent ID not found")
    parser.add_argument("--retry-delay", type=int, default=5, help="Seconds to wait between retries")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def get_current_agent_id(container_name, tail_lines=200, retry_count=3, retry_delay=5):
    """
    Extract the current Yona agent ID from Docker logs.
    
    Args:
        container_name: Name of the Docker container
        tail_lines: Number of log lines to check
        retry_count: Number of times to retry if agent ID not found
        retry_delay: Seconds to wait between retries
        
    Returns:
        str: The current Yona agent ID, or None if not found
    """
    logger.info(f"Extracting current agent ID from {container_name} logs")
    
    for attempt in range(retry_count):
        try:
            # Run docker logs command and capture output
            logger.info(f"Running docker logs command (attempt {attempt+1}/{retry_count})")
            result = subprocess.run(
                ["docker", "logs", container_name, "--tail", str(tail_lines)],
                capture_output=True, text=True, check=True
            )
            
            # Parse the logs to find the agent ID
            logger.info("Parsing logs to find agent ID")
            
            # Try different patterns to find the agent ID
            patterns = [
                r"Creating Coral adapter with session ID: (yona-agent-\d+)",
                r"Initialized Coral client with session ID: (yona-agent-\d+)",
                r"SSE URL: https://coral\.pushcollective\.club/devmode/default-app/public/(yona-agent-\d+)/sse"
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, result.stdout)
                if matches:
                    # Get the most recent match (likely the current agent ID)
                    agent_id = matches[-1]
                    logger.info(f"Found agent ID: {agent_id}")
                    return agent_id
            
            logger.warning(f"Agent ID not found in logs (attempt {attempt+1}/{retry_count})")
            
            if attempt < retry_count - 1:
                logger.info(f"Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running docker logs command: {e}")
            if attempt < retry_count - 1:
                logger.info(f"Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay)
    
    logger.error(f"Failed to find agent ID after {retry_count} attempts")
    return None

def test_with_agent_id(agent_id, args):
    """
    Test the Coral Protocol integration with the specified agent ID.
    
    Args:
        agent_id: The Yona agent ID to test with
        args: Command line arguments
        
    Returns:
        bool: True if the test was successful, False otherwise
    """
    logger.info(f"Starting test with agent ID: {agent_id}")
    
    # Create Coral client
    client = CoralClient(
        session_id=args.session_id,
        server_url=args.server_url,
        use_devmode=True
    )
    
    # Create a thread with both agents
    logger.info(f"Creating thread with agents: {agent_id} and {args.youtube_agent_id}")
    try:
        thread_id = client.create_thread([agent_id, args.youtube_agent_id])
        logger.info(f"Thread created with ID: {thread_id}")
    except Exception as e:
        logger.error(f"Failed to create thread: {str(e)}")
        return False
    
    # Send a message from YouTube agent to Yona with multiple mention formats
    logger.info(f"Sending message from {args.youtube_agent_id} to {agent_id}")
    
    # Try different mention formats
    message_content = (
        f"@{agent_id} Hey Yona, can you create a song about debugging? "
        f"Also trying alternate mention format: <@{agent_id}> "
        "I'd like a fun, upbeat song about fixing bugs and making things work. "
        "This is a test message from the auto-test script."
    )
    
    try:
        message_id = client.send_message(
            thread_id=thread_id,
            content=message_content,
            mentions=[agent_id]  # Explicit mention in the API call
        )
        logger.info(f"Message sent with ID: {message_id}")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return False
    
    # Wait for a while to see if Yona responds
    logger.info(f"Waiting for {args.wait_time} seconds to see if Yona responds...")
    logger.info("Check the Yona logs in another terminal with: docker logs -f yona_yona-coral_1")
    
    try:
        # Keep the script running to monitor for responses
        for i in range(args.wait_time):
            time.sleep(1)
            if i % 10 == 0:
                logger.info(f"Still waiting... {i}/{args.wait_time} seconds elapsed")
                
                # Check the logs for a response
                if i > 0:  # Skip the first check to give Yona time to respond
                    try:
                        result = subprocess.run(
                            ["docker", "logs", args.container_name, "--tail", "50"],
                            capture_output=True, text=True, check=True
                        )
                        
                        # Look for evidence of a response
                        response_patterns = [
                            r"Received message mention from",
                            r"Generating song concept from prompt",
                            r"Creating song with title",
                            r"Sending response to thread"
                        ]
                        
                        for pattern in response_patterns:
                            if re.search(pattern, result.stdout):
                                logger.info(f"Found evidence of response: {pattern}")
                                return True
                    except Exception as e:
                        logger.error(f"Error checking logs for response: {str(e)}")
    except KeyboardInterrupt:
        logger.info("Test interrupted")
    
    logger.info("Test completed, but no response detected")
    return False

def main():
    """Main function."""
    args = parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("coral_client").setLevel(logging.DEBUG)
    
    # Get the current agent ID
    agent_id = get_current_agent_id(
        args.container_name,
        args.tail_lines,
        args.retry_count,
        args.retry_delay
    )
    
    if not agent_id:
        logger.error("Could not determine the current agent ID. Exiting.")
        return 1
    
    # Test with the agent ID
    success = test_with_agent_id(agent_id, args)
    
    if success:
        logger.info("Test successful! Yona responded to the message.")
        return 0
    else:
        logger.warning("Test completed, but Yona did not respond to the message.")
        logger.info("Troubleshooting tips:")
        logger.info("1. Check if the fix_coral_adapter.py script was run")
        logger.info("2. Restart the Yona container and try again")
        logger.info("3. Check the Yona logs for errors")
        logger.info("4. Try with a simpler message")
        return 1

if __name__ == "__main__":
    sys.exit(main())
