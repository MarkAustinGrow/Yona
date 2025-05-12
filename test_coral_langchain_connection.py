#!/usr/bin/env python3
"""
Test script for connecting to the Coral server using LangChain MCP adapters.
This script follows the example provided by the Coral server team.
"""
import os
import sys
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

async def test_coral_connection(hostname="coral.pushcollective.club", port=5555, agent_id="yona", wait_for_agents=2):
    """
    Test connection to the Coral server using LangChain MCP adapters.
    
    Args:
        hostname: Hostname of the Coral server
        port: Port of the Coral server
        agent_id: ID to use for this agent
        wait_for_agents: Number of agents to wait for
    """
    try:
        # Import here to avoid errors if package is not installed
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Configure connection parameters
        base_url = f"http://{hostname}:{port}/devmode/exampleApplication/privkey/session1/sse"
        params = {
            "waitForAgents": wait_for_agents,
            "agentId": agent_id,
            "agentDescription": "Team Yona agent for music creation and feedback processing"
        }
        query_string = urllib.parse.urlencode(params)
        mcp_server_url = f"{base_url}?{query_string}"
        
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
            
            # List all registered agents
            print("\nListing agents on Coral server...")
            try:
                # Get the list_agents tool
                list_agents_tool = None
                for tool in tools:
                    if tool.name == "list_agents":
                        list_agents_tool = tool
                        break
                
                if list_agents_tool:
                    list_agents_result = await list_agents_tool.ainvoke({"includeDetails": True})
                else:
                    raise ValueError("list_agents tool not found")
                print(f"Registered agents: {list_agents_result}")
                
                # Look for other agents
                if isinstance(list_agents_result, dict) and "agents" in list_agents_result:
                    agents_list = list_agents_result.get("agents", [])
                    if isinstance(agents_list, list):
                        if len(agents_list) > 0:
                            print(f"\nFound {len(agents_list)} agents:")
                            for agent in agents_list:
                                print(f"  - {agent.get('id')}: {agent.get('description', 'No description')}")
                            
                            # Create a thread with all agents
                            print("\nCreating a thread with all agents...")
                            participant_ids = [agent.get("id") for agent in agents_list]
                            if agent_id not in participant_ids:
                                participant_ids.append(agent_id)
                                
                            # Get the create_thread tool
                            create_thread_tool = None
                            for tool in tools:
                                if tool.name == "create_thread":
                                    create_thread_tool = tool
                                    break
                            
                            if create_thread_tool:
                                thread_result = await create_thread_tool.ainvoke({
                                    "threadName": "Yona Test Thread",
                                    "participantIds": participant_ids
                                })
                            else:
                                raise ValueError("create_thread tool not found")
                            print(f"Thread creation result: {thread_result}")
                            
                            thread_id = thread_result.get("threadId")
                            if thread_id:
                                print(f"Created thread with ID: {thread_id}")
                                
                                # Send a message to the thread
                                print("\nSending a message to the thread...")
                                send_message_tool = None
                                for tool in tools:
                                    if tool.name == "send_message":
                                        send_message_tool = tool
                                        break
                                
                                if send_message_tool:
                                    message_result = await send_message_tool.ainvoke({
                                        "threadId": thread_id,
                                        "content": "Hello from Yona! This is a test message.",
                                        "mentions": participant_ids
                                    })
                                    print(f"Message sent: {message_result}")
                                    
                                    # Wait for a response
                                    print("\nWaiting for a response (30 seconds timeout)...")
                                    wait_for_mentions_tool = None
                                    for tool in tools:
                                        if tool.name == "wait_for_mentions":
                                            wait_for_mentions_tool = tool
                                            break
                                    
                                    if wait_for_mentions_tool:
                                        try:
                                            mentions_result = await wait_for_mentions_tool.ainvoke({
                                                "timeoutMs": 30000  # 30 seconds
                                            })
                                            print(f"Received mentions: {mentions_result}")
                                        except Exception as e:
                                            print(f"No response received within timeout: {str(e)}")
                                    else:
                                        print("wait_for_mentions tool not found")
                                else:
                                    print("send_message tool not found")
                            else:
                                print("Failed to get thread ID from result")
                        else:
                            print("No other agents found")
                    else:
                        print("Unexpected agents list format")
                else:
                    print("No agents found or unexpected response format")
            except Exception as e:
                print(f"Error invoking tool: {str(e)}")
        
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
    parser = argparse.ArgumentParser(description='Test Coral Protocol using LangChain MCP adapters')
    
    # Add arguments
    parser.add_argument('--hostname', type=str, default="coral.pushcollective.club",
                        help='Hostname of the Coral server')
    parser.add_argument('--port', type=int, default=5555,
                        help='Port of the Coral server')
    parser.add_argument('--agent-id', type=str, default="yona",
                        help='ID to use for this agent')
    parser.add_argument('--wait-for-agents', type=int, default=2,
                        help='Number of agents to wait for')
    
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(test_coral_connection(
        args.hostname,
        args.port,
        args.agent_id,
        args.wait_for_agents
    ))

if __name__ == "__main__":
    main()
