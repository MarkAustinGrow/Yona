#!/usr/bin/env python3
"""
Debug script for Coral Protocol integration.
This script attempts to connect to the Coral server and send a message to Yona
with enhanced debugging to diagnose communication issues.
"""

import logging
import time
import argparse
import json
import requests
import threading
from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG level for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("coral_debug")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Debug Coral Protocol integration")
    parser.add_argument("--yona-agent-id", default="yona-agent-1745932063", help="Yona agent ID")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--wait-time", type=int, default=60, help="Time to wait after sending message (seconds)")
    parser.add_argument("--session-id", default=f"debug-session-{int(time.time())}", help="Session ID for the test")
    parser.add_argument("--find-threads", action="store_true", help="Try to find existing threads")
    return parser.parse_args()

def find_yona_thread(client, yona_agent_id):
    """
    Attempt to find an existing thread created by Yona.
    This is a workaround since the Coral API doesn't directly support listing threads.
    """
    logger.info(f"Attempting to find a thread with Yona agent: {yona_agent_id}")
    
    # First, try to list agents to confirm Yona is registered
    try:
        agents = client.list_agents()
        if agents:
            logger.info(f"Found {len(agents)} agents:")
            for agent in agents:
                logger.info(f"  - {agent.get('name')} (ID: {agent.get('id')})")
                if yona_agent_id in str(agent.get('id')):
                    logger.info(f"Found Yona agent: {agent}")
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
    
    # Create a new thread with Yona
    logger.info(f"Creating a new thread with Yona agent: {yona_agent_id}")
    try:
        thread_id = client.create_thread([yona_agent_id])
        logger.info(f"Created thread with ID: {thread_id}")
        return thread_id
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}")
        return None

def monitor_sse_events(client, yona_agent_id, thread_id):
    """
    Monitor SSE events to see if Yona is responding.
    """
    logger.info("Starting SSE event monitor")
    
    def event_handler(event_data):
        logger.info(f"Received event: {json.dumps(event_data, indent=2)}")
        
        # Check if this is a message from Yona
        if event_data.get("type") == "message" and event_data.get("sender_id") == yona_agent_id:
            logger.info(f"Received message from Yona: {event_data.get('content')}")
    
    # Start listening for events
    client.event_handlers = {
        "message": event_handler,
        "tool_response": lambda data: logger.info(f"Tool response: {json.dumps(data, indent=2)}")
    }
    
    return client.start_listening()

def main():
    """Main function to run the debug script."""
    args = parse_args()
    
    logger.info("Starting Coral Protocol debug script")
    logger.info(f"Yona Agent ID: {args.yona_agent_id}")
    
    # Create Coral client with verbose logging
    client = CoralClient(
        session_id=args.session_id,
        server_url=args.server_url,
        use_devmode=True
    )
    
    # Start monitoring SSE events
    monitor_thread = monitor_sse_events(client, args.yona_agent_id, None)
    
    # Find or create a thread with Yona
    thread_id = find_yona_thread(client, args.yona_agent_id)
    if not thread_id:
        logger.error("Failed to find or create a thread with Yona")
        return
    
    # Send a message to Yona with different mention formats to test
    logger.info(f"Sending test message to thread: {thread_id}")
    
    # Try different mention formats to see which one works
    message_content = (
        f"@{args.yona_agent_id} Hey Yona, can you create a song about debugging? "
        f"Also trying alternate mention format: <@{args.yona_agent_id}> "
        "I'd like a fun, upbeat song about fixing bugs and making things work. "
        "This is a test message from the debug script."
    )
    
    try:
        message_id = client.send_message(
            thread_id=thread_id,
            content=message_content,
            mentions=[args.yona_agent_id]  # Explicit mention in the API call
        )
        logger.info(f"Message sent with ID: {message_id}")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return
    
    # Wait and monitor for responses
    logger.info(f"Waiting for {args.wait_time} seconds to see if Yona responds...")
    logger.info("Check the Yona logs in another terminal with: docker logs -f yona_yona-coral_1")
    
    try:
        # Keep the script running to monitor for responses
        for i in range(args.wait_time):
            time.sleep(1)
            if i % 10 == 0:
                logger.info(f"Still waiting... {i}/{args.wait_time} seconds elapsed")
    except KeyboardInterrupt:
        logger.info("Debug script interrupted")
    
    logger.info("Debug test completed")
    logger.info("If Yona didn't respond, check the following:")
    logger.info("1. Verify the agent ID is correct")
    logger.info("2. Check if the SSE connection is stable")
    logger.info("3. Examine the Yona logs for any errors in message processing")
    logger.info("4. Verify the mention format is recognized by the Yona agent")

if __name__ == "__main__":
    main()
