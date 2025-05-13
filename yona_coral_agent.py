#!/usr/bin/env python3
"""
YonaCoralAgent - Agent for communicating with Team Angus via Coral Protocol

This module implements the YonaCoralAgent class, which connects to the Coral Protocol
server and listens for function calls from Team Angus. It uses the YonaAgent class
to create songs based on prompts received from Team Angus.
"""
import os
import sys
import json
import logging
import uuid
import asyncio
from datetime import datetime
import urllib.parse
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

# Import the YonaAgent class
try:
    from src.agent import YonaAgent
except ImportError:
    print("Error: YonaAgent class not found.")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YonaCoralAgent:
    """
    YonaCoralAgent connects to the Coral Protocol server and listens for function calls
    from Team Angus. It uses the YonaAgent class to create songs based on prompts
    received from Team Angus.
    """
    
    def __init__(self, server_url=None, agent_id=None, openai_api_key=None):
        """
        Initialize the YonaCoralAgent.
        
        Args:
            server_url: URL of the Coral server (default: http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse)
            agent_id: ID to use for this agent (default: yona_agent)
            openai_api_key: API key for OpenAI (default: loaded from environment)
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Set default values
        self.server_url = server_url or "http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"
        self.agent_id = agent_id or "yona_agent"
        
        # Get the OpenAI API key
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.error("Neither OPENAI_KEY nor OPENAI_API_KEY environment variables are set")
            raise ValueError("Neither OPENAI_KEY nor OPENAI_API_KEY environment variables are set")
        
        # Initialize the YonaAgent
        self.yona_agent = YonaAgent(openai_api_key=self.openai_api_key)
        
        # Initialize client
        self.client = None
        
        logger.info(f"YonaCoralAgent initialized with agent ID: {self.agent_id}")
    
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
                "agentId": self.agent_id,  # Use yona_agent as the agent ID
                "agentDescription": "Yona agent for creating songs and other creative content"  # Description of capabilities
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
    
    async def wait_for_mentions(self, timeout_ms=30000):
        """
        Wait for mentions from other agents.
        
        Args:
            timeout_ms: Timeout in milliseconds (default: 30000)
            
        Returns:
            list: List of mentions
        """
        try:
            mentions = await self.client.connections["coral"].invoke_tool("wait_for_mentions", {
                "timeoutMs": timeout_ms
            })
            
            if mentions:
                logger.info(f"Received {len(mentions)} mentions")
                for mention in mentions:
                    await self.process_mention(mention)
            else:
                logger.debug("No mentions received within timeout")
            
            return mentions
        except Exception as e:
            logger.error(f"Error waiting for mentions: {e}")
            return []
    
    async def process_mention(self, mention):
        """
        Process a mention from another agent.
        
        Args:
            mention: Mention object from the Coral server
        """
        try:
            # Extract content and parse JSON
            content = mention.get("content", "{}")
            message = json.loads(content)
            
            logger.info(f"Processing mention: {message}")
            
            # Check if it's a function call
            if message.get("type") == "function_call":
                function_name = message.get("function")
                arguments = message.get("arguments", {})
                
                # Handle different functions
                if function_name == "create_song":
                    prompt = arguments.get("prompt", "")
                    result = self.create_song(prompt)
                    await self.send_response(mention, function_name, result, message)
                else:
                    # Unknown function
                    error_message = f"Unknown function: {function_name}"
                    await self.send_error(mention, function_name, error_message, message)
            else:
                # Not a function call
                logger.warning(f"Received message is not a function call: {message}")
        except json.JSONDecodeError:
            # Invalid JSON
            logger.error(f"Invalid JSON in mention: {mention.get('content')}")
            await self.send_error(mention, "unknown", "Invalid JSON in message", None)
        except Exception as e:
            # Other errors
            logger.error(f"Error processing mention: {e}")
            await self.send_error(mention, "unknown", f"Error processing message: {str(e)}", None)
    
    async def send_response(self, mention, function_name, result, original_message):
        """
        Send a response to a function call.
        
        Args:
            mention: Mention object from the Coral server
            function_name: Name of the function that was called
            result: Result of the function call
            original_message: Original message from the caller
        """
        try:
            # Create response message
            response = {
                "type": "function_response",
                "function": function_name,
                "result": result,
                "metadata": {
                    "sender": self.agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "correlation_id": original_message.get("metadata", {}).get("message_id")
                }
            }
            
            # Send the response
            await self.client.connections["coral"].invoke_tool("send_message", {
                "threadId": mention.get("threadId"),
                "content": json.dumps(response),
                "mentions": [original_message.get("metadata", {}).get("sender")]
            })
            
            logger.info(f"Sent response for function: {function_name}")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    async def send_error(self, mention, function_name, error_message, original_message):
        """
        Send an error response.
        
        Args:
            mention: Mention object from the Coral server
            function_name: Name of the function that was called
            error_message: Error message
            original_message: Original message from the caller
        """
        try:
            # Create error message
            error = {
                "type": "error",
                "function": function_name,
                "error": error_message,
                "metadata": {
                    "sender": self.agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "correlation_id": original_message.get("metadata", {}).get("message_id") if original_message else None
                }
            }
            
            # Send the error
            await self.client.connections["coral"].invoke_tool("send_message", {
                "threadId": mention.get("threadId"),
                "content": json.dumps(error),
                "mentions": [original_message.get("metadata", {}).get("sender") if original_message else "angus_agent"]
            })
            
            logger.info(f"Sent error for function: {function_name}")
        except Exception as e:
            logger.error(f"Error sending error response: {e}")
    
    def create_song(self, prompt):
        """
        Create a song based on a prompt.
        
        Args:
            prompt: Prompt for the song
            
        Returns:
            dict: Song data
        """
        logger.info(f"Creating song with prompt: {prompt}")
        
        try:
            # Generate a song concept
            concept = self.yona_agent.generate_song_concept(prompt)
            
            # Generate lyrics
            lyrics = self.yona_agent.generate_lyrics(concept)
            
            # Create the song
            song_data = self.yona_agent.create_song(
                title=concept.get('title'),
                lyrics=lyrics,
                style=concept.get('style_tags'),
                negative_tags=concept.get('negative_tags'),
                make_instrumental=concept.get('make_instrumental', False),
                mv=concept.get('mv_type', 'sonic-v4'),
                gpt_description_prompt=concept.get('description'),
                voice_gender="female"  # Hard-coded as female
            )
            
            # Extract relevant data for the response
            result = {
                "title": song_data.get('title'),
                "audio_url": song_data.get('audio_url'),
                "video_url": song_data.get('video_url'),
                "image_url": song_data.get('image_url'),
                "lyrics": song_data.get('lyrics'),
                "created_at": datetime.utcnow().isoformat()
            }
            
            return result
        except Exception as e:
            logger.error(f"Error creating song: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }

async def main():
    """
    Main function.
    """
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Yona Coral Agent')
    parser.add_argument('--server-url', type=str, 
                        default="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse",
                        help='URL of the Coral server')
    parser.add_argument('--agent-id', type=str, default="yona_agent",
                        help='ID to use for this agent')
    args = parser.parse_args()
    
    # Create the Yona Coral agent
    agent = YonaCoralAgent(
        server_url=args.server_url,
        agent_id=args.agent_id
    )
    
    # Connect to the server
    if not await agent.connect():
        logger.error("Failed to connect to the server")
        return
    
    try:
        # List connected agents
        agents = await agent.list_agents()
        
        # Main loop: wait for mentions and process them
        while True:
            await agent.wait_for_mentions(30000)  # 30 seconds timeout
            await asyncio.sleep(1)  # Small delay to prevent tight loop
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Disconnect from the server
        await agent.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
