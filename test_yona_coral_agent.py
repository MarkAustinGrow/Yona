#!/usr/bin/env python3
"""
Test script for the Yona Coral Agent.

This script simulates function calls from Team Angus to test the Yona Coral Agent.
It connects to the Coral Protocol server, creates a thread with the Yona agent,
and sends a function call to create a song.
"""
import os
import sys
import json
import logging
import uuid
import asyncio
from datetime import datetime
import urllib.parse
import argparse
from typing import Dict, Any, Optional, List, Union

# Import the langchain_mcp_adapters client
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:
    print("Error: langchain_mcp_adapters package not installed.")
    print("Please install it with: pip install langchain_mcp_adapters==0.0.10")
    sys.exit(1)

# Import the dotenv package for loading environment variables
try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv package not installed.")
    print("Please install it with: pip install python-dotenv")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AngusSimulator:
    """
    AngusSimulator simulates the Angus agent for testing the Yona Coral Agent.
    """
    
    def __init__(self, server_url=None, agent_id=None, target_agent_id=None):
        """
        Initialize the AngusSimulator.
        
        Args:
            server_url: URL of the Coral server (default: http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse)
            agent_id: ID to use for this agent (default: angus_agent)
            target_agent_id: ID of the target agent (default: yona_agent)
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Set default values
        self.server_url = server_url or "http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"
        self.agent_id = agent_id or "angus_agent"
        self.target_agent_id = target_agent_id or "yona_agent"
        
        # Initialize client
        self.client = None
        self.thread_id = None
        
        logger.info(f"AngusSimulator initialized with agent ID: {self.agent_id}")
    
    async def connect(self):
        """
        Connect to the Coral server.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Configure connection parameters
            params = {
                "waitForAgents": 2,  # Wait for both agents to be connected
                "agentId": self.agent_id,  # Use angus_agent as the agent ID
                "agentDescription": "Angus agent for testing the Yona Coral Agent"  # Description of capabilities
            }
            
            # Encode parameters and create the full URL
            query_string = urllib.parse.urlencode(params)
            mcp_server_url = f"{self.server_url}?{query_string}"
            
            logger.info(f"Connecting to Coral server at {mcp_server_url}")
            
            # Connect to the server
            self.client = MultiServerMCPClient(
                connections={
                    "coral": {
                        "transport": "sse",
                        "url": mcp_server_url,
                        "timeout": 300,
                        "sse_read_timeout": 300,
                    }
                }
            )
            await self.client.__aenter__()
            logger.info(f"Connected to Coral server at {mcp_server_url}")
            
            # Start the heartbeat task
            asyncio.create_task(self.heartbeat())
            
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self):
        """
        Disconnect from the Coral server.
        """
        if self.client:
            await self.client.__aexit__(None, None, None)
            logger.info("Disconnected from Coral server")
    
    async def heartbeat(self):
        """
        Send periodic heartbeats to keep the connection alive.
        """
        while True:
            try:
                await asyncio.sleep(60)  # Send heartbeat every 60 seconds
                if self.client:
                    await self.client.connections["coral"].invoke_tool("list_agents", {
                        "includeDetails": True
                    })
                    logger.debug("Heartbeat sent")
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def list_agents(self):
        """
        List all connected agents.
        
        Returns:
            list: List of connected agents
        """
        try:
            result = await self.client.connections["coral"].invoke_tool("list_agents", {
                "includeDetails": True
            })
            logger.info(f"Connected agents: {result}")
            return result
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return []
    
    async def create_thread(self):
        """
        Create a thread with the target agent.
        
        Returns:
            str: Thread ID
        """
        try:
            result = await self.client.connections["coral"].invoke_tool("create_thread", {
                "threadName": f"Test Thread {uuid.uuid4()}",
                "participantIds": [self.agent_id, self.target_agent_id]
            })
            
            self.thread_id = result.get("threadId")
            logger.info(f"Created thread: {self.thread_id}")
            return self.thread_id
        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            return None
    
    async def send_function_call(self, function_name, arguments):
        """
        Send a function call to the target agent.
        
        Args:
            function_name: Name of the function to call
            arguments: Arguments for the function
            
        Returns:
            dict: Response from the target agent
        """
        if not self.thread_id:
            logger.error("No thread ID available. Create a thread first.")
            return None
        
        try:
            # Create the message
            message = {
                "type": "function_call",
                "function": function_name,
                "arguments": arguments,
                "metadata": {
                    "sender": self.agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message_id": str(uuid.uuid4())
                }
            }
            
            # Send the message
            await self.client.connections["coral"].invoke_tool("send_message", {
                "threadId": self.thread_id,
                "content": json.dumps(message),
                "mentions": [self.target_agent_id]
            })
            
            logger.info(f"Sent function call: {function_name}")
            
            # Wait for a response
            response = await self.wait_for_response(60000)  # 60 seconds timeout
            return response
        except Exception as e:
            logger.error(f"Error sending function call: {e}")
            return None
    
    async def wait_for_response(self, timeout_ms=30000):
        """
        Wait for a response from the target agent.
        
        Args:
            timeout_ms: Timeout in milliseconds (default: 30000)
            
        Returns:
            dict: Response from the target agent
        """
        try:
            mentions = await self.client.connections["coral"].invoke_tool("wait_for_mentions", {
                "timeoutMs": timeout_ms
            })
            
            if not mentions:
                logger.warning("No response received within timeout")
                return None
            
            # Process the first mention
            mention = mentions[0]
            try:
                content = mention.get("content", "{}")
                message = json.loads(content)
                logger.info(f"Received response: {message}")
                return message
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in response: {content}")
                return None
        except Exception as e:
            logger.error(f"Error waiting for response: {e}")
            return None

async def main():
    """
    Main function.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Test the Yona Coral Agent')
    parser.add_argument('--server-url', type=str, 
                        default="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse",
                        help='URL of the Coral server')
    parser.add_argument('--agent-id', type=str, default="angus_agent",
                        help='ID to use for this agent')
    parser.add_argument('--target-agent-id', type=str, default="yona_agent",
                        help='ID of the target agent')
    parser.add_argument('--prompt', type=str, default="Create a happy K-pop song about summer adventures",
                        help='Prompt for the song')
    args = parser.parse_args()
    
    # Create the Angus simulator
    simulator = AngusSimulator(
        server_url=args.server_url,
        agent_id=args.agent_id,
        target_agent_id=args.target_agent_id
    )
    
    # Connect to the server
    if not await simulator.connect():
        logger.error("Failed to connect to the server")
        return
    
    try:
        # List connected agents
        agents = await simulator.list_agents()
        
        # Check if the target agent is connected
        target_agent_found = False
        for agent in agents:
            if agent.get("agentId") == simulator.target_agent_id:
                target_agent_found = True
                break
        
        if not target_agent_found:
            logger.warning(f"Target agent {simulator.target_agent_id} not found. Waiting for it to connect...")
            # Wait for a while and try again
            await asyncio.sleep(10)
            agents = await simulator.list_agents()
            for agent in agents:
                if agent.get("agentId") == simulator.target_agent_id:
                    target_agent_found = True
                    break
        
        if not target_agent_found:
            logger.error(f"Target agent {simulator.target_agent_id} not found. Make sure it's running.")
            return
        
        # Create a thread
        thread_id = await simulator.create_thread()
        if not thread_id:
            logger.error("Failed to create a thread")
            return
        
        # Send a function call to create a song
        logger.info(f"Sending function call to create a song with prompt: {args.prompt}")
        response = await simulator.send_function_call("create_song", {
            "prompt": args.prompt
        })
        
        if response:
            logger.info("Function call successful!")
            logger.info(f"Response type: {response.get('type')}")
            
            if response.get("type") == "function_response":
                result = response.get("result", {})
                logger.info(f"Song title: {result.get('title')}")
                logger.info(f"Audio URL: {result.get('audio_url')}")
                logger.info(f"Video URL: {result.get('video_url')}")
                logger.info(f"Image URL: {result.get('image_url')}")
            elif response.get("type") == "error":
                logger.error(f"Error: {response.get('error')}")
        else:
            logger.error("Function call failed or timed out")
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Disconnect from the server
        await simulator.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
