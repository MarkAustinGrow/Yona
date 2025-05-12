#!/usr/bin/env python3
"""
Test script for communicating with the Coral Protocol server using MCP adapters.
This script attempts to discover and communicate with agent Angus.
"""
import os
import json
import logging
import argparse
import asyncio
import urllib.parse
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_coral_connection(server_url, agent_id="yona", wait_for_agents=2):
    """
    Test connection to the Coral server using MCP adapters.
    
    Args:
        server_url: Base URL of the Coral server (without query parameters)
        agent_id: ID to use for this agent
        wait_for_agents: Number of agents to wait for
    """
    try:
        # Import here to avoid errors if package is not installed
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Configure connection parameters
        params = {
            "waitForAgents": wait_for_agents,
            "agentId": agent_id,
            "agentDescription": "Yona AI Agent for music creation and feedback processing"
        }
        query_string = urllib.parse.urlencode(params)
        mcp_server_url = f"{server_url}?{query_string}"
        
        print(f"\n=== Testing Coral Protocol Connection to {mcp_server_url} ===\n")
        
        async with MultiServerMCPClient(
            connections={
                "coral": {
                    "transport": "sse",
                    "url": mcp_server_url,
                    "timeout": 300,
                    "sse_read_timeout": 300,
                }
            }
        ) as client:
            # Get available tools
            print("\nGetting available tools...")
            tools = client.get_tools()
            print(f"Available tools: {tools}")
            
            # Find tools by name
            list_agents_tool = None
            create_thread_tool = None
            send_message_tool = None
            wait_for_mentions_tool = None
            
            for tool in tools:
                if tool.name == "list_agents":
                    list_agents_tool = tool
                elif tool.name == "create_thread":
                    create_thread_tool = tool
                elif tool.name == "send_message":
                    send_message_tool = tool
                elif tool.name == "wait_for_mentions":
                    wait_for_mentions_tool = tool
            
            # List all registered agents
            print("\nListing agents on Coral server...")
            if list_agents_tool:
                list_agents_result = await list_agents_tool.ainvoke({"includeDetails": True})
                print(f"Registered agents: {list_agents_result}")
                
                # Look for Angus agent
                angus_agent = None
                
                # Handle different response formats
                if isinstance(list_agents_result, dict) and "agents" in list_agents_result:
                    agents_list = list_agents_result.get("agents", [])
                    if isinstance(agents_list, list):
                        for agent in agents_list:
                            if isinstance(agent, dict) and agent.get("id") == "69943c74-0cb8-5911-98db-79cca0bf8b7d":
                                angus_agent = agent
                                break
                else:
                    print("No agents found or unexpected response format")
                
                if angus_agent:
                    print(f"\nFound Angus agent: {angus_agent}")
                    
                    # Create a thread with Angus
                    if create_thread_tool:
                        print("\nCreating a thread with Angus...")
                        thread_result = await create_thread_tool.ainvoke({
                            "threadName": "Yona-Angus Test Thread",
                            "participantIds": [agent_id, angus_agent.get("id")]
                        })
                        print(f"Thread creation result: {thread_result}")
                        
                        thread_id = thread_result.get("thread_id")
                        if thread_id:
                            print(f"Created thread with ID: {thread_id}")
                            
                            # Send a message to Angus
                            if send_message_tool:
                                print("\nSending a message to Angus...")
                                message_result = await send_message_tool.ainvoke({
                                    "threadId": thread_id,
                                    "content": "Hello from Yona! Can you tell me about your capabilities?",
                                    "mentions": [angus_agent.get("id")]
                                })
                                print(f"Message sent: {message_result}")
                                
                                # Wait for a response
                                if wait_for_mentions_tool:
                                    print("\nWaiting for a response from Angus...")
                                    mentions_result = await wait_for_mentions_tool.ainvoke({
                                        "timeoutMs": 30000  # 30 seconds
                                    })
                                    print(f"Received mentions: {mentions_result}")
                                else:
                                    print("Wait for mentions tool not found")
                            else:
                                print("Send message tool not found")
                        else:
                            print("Failed to get thread ID from result")
                    else:
                        print("Create thread tool not found")
                else:
                    print("Angus agent not found")
            else:
                print("List agents tool not found")
        
        return True
    except ImportError as e:
        logger.error(f"Required package not installed: {str(e)}")
        print(f"\nError: Required package not installed: {str(e)}")
        print("\nPlease install the required packages:")
        print("pip install langchain langchain_mcp_adapters langchain-openai")
        return False
    except Exception as e:
        logger.error(f"Error testing Coral connection: {str(e)}")
        print(f"\nError testing Coral connection: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test Coral Protocol using MCP adapters')
    
    # Add arguments
    parser.add_argument('--server-url', type=str, 
                        default="http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse",
                        help='Base URL of the Coral server (without query parameters)')
    parser.add_argument('--agent-id', type=str, default="yona",
                        help='ID to use for this agent')
    parser.add_argument('--wait-for-agents', type=int, default=2,
                        help='Number of agents to wait for')
    
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(test_coral_connection(
        args.server_url,
        args.agent_id,
        args.wait_for_agents
    ))

if __name__ == "__main__":
    main()
