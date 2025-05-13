#!/usr/bin/env python3
"""
Test script for the Enhanced Yona Coral Agent.

This script simulates function calls from Team Angus to test the Enhanced Yona Coral Agent.
It connects to the Coral Protocol server, creates a thread with the Yona agent,
and sends a function call to create a song.

The enhanced version includes better handling of string mentions and thread management.
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
    AngusSimulator simulates the Angus agent for testing the Enhanced Yona Coral Agent.
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
        
        # Enhanced features
        self.thread_cache = {}  # Map of agent_id -> thread_id
        
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
                    tools = self.client.get_tools()
                    list_agents_tool = [t for t in tools if t.name == "list_agents"][0]
                    await list_agents_tool.ainvoke({"includeDetails": True})
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
            tools = self.client.get_tools()
            list_agents_tool = [t for t in tools if t.name == "list_agents"][0]
            result = await list_agents_tool.ainvoke({"includeDetails": True})
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
            tools = self.client.get_tools()
            create_thread_tool = [t for t in tools if t.name == "create_thread"][0]
            result = await create_thread_tool.ainvoke({
                "threadName": f"Test Thread {uuid.uuid4()}",
                "participantIds": [self.agent_id, self.target_agent_id]
            })
            
            # Handle both string and dictionary results
            if isinstance(result, dict):
                self.thread_id = result.get("threadId")
            elif isinstance(result, str):
                # Try to parse the string as JSON
                try:
                    thread_data = json.loads(result)
                    self.thread_id = thread_data.get("threadId")
                except json.JSONDecodeError:
                    # If it's not valid JSON, use the string itself as the thread ID
                    self.thread_id = result
            else:
                logger.error(f"Unexpected result type from create_thread: {type(result)}")
                return None
            
            # Cache the thread ID
            if self.thread_id:
                self.thread_cache[self.target_agent_id] = self.thread_id
            
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
            tools = self.client.get_tools()
            send_message_tool = [t for t in tools if t.name == "send_message"][0]
            await send_message_tool.ainvoke({
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
            tools = self.client.get_tools()
            wait_for_mentions_tool = [t for t in tools if t.name == "wait_for_mentions"][0]
            
            # Initialize mention buffer for aggregating fragmented mentions
            mention_buffer = ""
            
            # Wait for mentions with timeout
            start_time = datetime.now()
            end_time = start_time + datetime.timedelta(milliseconds=timeout_ms)
            
            while datetime.now() < end_time:
                remaining_ms = int((end_time - datetime.now()).total_seconds() * 1000)
                if remaining_ms <= 0:
                    break
                
                mentions = await wait_for_mentions_tool.ainvoke({"timeoutMs": min(remaining_ms, 5000)})
                
                if not mentions:
                    # No mentions received, wait a bit and try again
                    await asyncio.sleep(1)
                    continue
                
                # Log detailed information about the mentions
                logger.debug(f"Received {len(mentions)} mentions")
                logger.debug(f"Mentions type: {type(mentions)}")
                if isinstance(mentions, list) and len(mentions) > 0:
                    logger.debug(f"First mention type: {type(mentions[0])}")
                    logger.debug(f"First mention content: {mentions[0]}")
                
                # Check if we have single-character mentions (fragmented)
                if all(isinstance(m, str) and len(m.strip()) <= 1 for m in mentions):
                    # These might be fragments of a single message
                    mention_buffer += "".join(mentions)
                    logger.debug(f"Aggregated mention buffer: {mention_buffer}")
                    
                    # Try to parse the buffer as JSON
                    try:
                        message = json.loads(mention_buffer)
                        logger.info(f"Successfully parsed aggregated mentions: {message}")
                        return message
                    except json.JSONDecodeError:
                        # Not valid JSON yet, keep buffering
                        logger.debug("Mention buffer not yet valid JSON")
                        continue
                
                # Process regular mentions
                for mention in mentions:
                    try:
                        # Extract content based on mention type
                        if isinstance(mention, str):
                            # If mention is a string, it's likely already the content
                            content = mention
                        elif isinstance(mention, dict):
                            # If mention is a dictionary, extract content
                            content = mention.get("content", "{}")
                        else:
                            # Unexpected type
                            logger.error(f"Unexpected mention type: {type(mention)}")
                            continue
                        
                        # Parse the content as JSON
                        message = json.loads(content)
                        logger.info(f"Received response: {message}")
                        return message
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in response: {mention if isinstance(mention, str) else mention.get('content')}")
                        continue
            
            logger.warning("No valid response received within timeout")
            return None
        except Exception as e:
            logger.error(f"Error waiting for response: {e}")
            return None
    
    async def test_fragmented_messages(self):
        """
        Test the agent's ability to handle fragmented messages.
        
        Returns:
            bool: True if the test was successful, False otherwise
        """
        if not self.thread_id:
            logger.error("No thread ID available. Create a thread first.")
            return False
        
        try:
            # Create a message that will be sent character by character
            message = {
                "type": "function_call",
                "function": "create_song",
                "arguments": {
                    "prompt": "Create a happy K-pop song about summer adventures"
                },
                "metadata": {
                    "sender": self.agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message_id": str(uuid.uuid4())
                }
            }
            
            message_json = json.dumps(message)
            
            # Send the message character by character
            tools = self.client.get_tools()
            send_message_tool = [t for t in tools if t.name == "send_message"][0]
            
            logger.info("Sending fragmented message character by character")
            for char in message_json:
                await send_message_tool.ainvoke({
                    "threadId": self.thread_id,
                    "content": char,
                    "mentions": [self.target_agent_id]
                })
                await asyncio.sleep(0.1)  # Small delay between characters
            
            logger.info("Fragmented message sent, waiting for response")
            
            # Wait for a response
            response = await self.wait_for_response(60000)  # 60 seconds timeout
            
            if response and response.get("type") == "function_response":
                logger.info("Successfully received response to fragmented message")
                return True
            else:
                logger.error("Failed to receive proper response to fragmented message")
                return False
        except Exception as e:
            logger.error(f"Error in fragmented message test: {e}")
            return False

async def main():
    """
    Main function.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Test the Enhanced Yona Coral Agent')
    parser.add_argument('--server-url', type=str, 
                        default="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse",
                        help='URL of the Coral server')
    parser.add_argument('--agent-id', type=str, default="angus_agent",
                        help='ID to use for this agent')
    parser.add_argument('--target-agent-id', type=str, default="yona_agent",
                        help='ID of the target agent')
    parser.add_argument('--prompt', type=str, default="Create a happy K-pop song about summer adventures",
                        help='Prompt for the song')
    parser.add_argument('--test-fragmented', action='store_true',
                        help='Test fragmented message handling')
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
        
        if args.test_fragmented:
            # Test fragmented message handling
            logger.info("Testing fragmented message handling...")
            success = await simulator.test_fragmented_messages()
            if success:
                logger.info("Fragmented message test passed!")
            else:
                logger.error("Fragmented message test failed!")
        else:
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
                    logger.info(f"Lyrics: {result.get('lyrics')}")
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
