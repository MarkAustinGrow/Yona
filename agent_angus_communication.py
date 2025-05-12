#!/usr/bin/env python3
"""
Script for communicating with Agent Angus via the Coral Protocol server.
This script uses the agent-based approach recommended by Team Angus.
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

async def connect_to_angus(server_url, agent_id="yona", wait_for_agents=2):
    """
    Connect to the Coral server and communicate with Agent Angus.
    
    Args:
        server_url: Base URL of the Coral server (without query parameters)
        agent_id: ID to use for this agent
        wait_for_agents: Number of agents to wait for
    """
    try:
        # Import here to avoid errors if package is not installed
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        # Configure connection parameters
        params = {
            "agentId": agent_id,
            "waitForAgents": wait_for_agents,
            "agentDescription": "Yona is a music creation agent that can generate songs based on feedback"
        }
        query_string = urllib.parse.urlencode(params)
        mcp_server_url = f"{server_url}?{query_string}"
        
        print(f"\n=== Connecting to Coral Protocol Server at {mcp_server_url} ===\n")
        
        # Create the OpenAI model with API key from environment
        import os
        from dotenv import load_dotenv
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Get the OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        model = ChatOpenAI(temperature=0, api_key=openai_api_key)
        
        # Create the agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are Yona, a music creation agent that can generate songs based on feedback. "
                      "You are connected to the Coral Protocol server and can communicate with other agents. "
                      "Your goal is to establish communication with Agent Angus and collaborate on music creation."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Connect to the Coral server
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
            # Get tools from the client
            print("\nGetting available tools...")
            tools = client.get_tools()
            print(f"Available tools: {tools}")
            
            # Create an agent with those tools
            print("\nCreating agent with tools...")
            agent = create_tool_calling_agent(model, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            # Run the agent with initial instructions
            print("\nRunning agent to communicate with Angus...")
            result = await agent_executor.ainvoke({
                "input": "Please perform the following tasks:\n"
                         "1. List all registered agents on the Coral server\n"
                         "2. Look for an agent with 'angus' in its ID or description\n"
                         "3. If found, create a thread with that agent\n"
                         "4. Send a message introducing yourself and asking about their capabilities\n"
                         "5. Wait for a response\n",
                "chat_history": []
            })
            
            print(f"\nAgent execution result: {result}")
        
        return True
    except ImportError as e:
        logger.error(f"Required package not installed: {str(e)}")
        print(f"\nError: Required package not installed: {str(e)}")
        print("\nPlease install the required packages:")
        print("pip install langchain==0.1.0 langchain_mcp_adapters==0.0.10 langchain-openai==0.0.2")
        return False
    except Exception as e:
        logger.error(f"Error connecting to Angus: {str(e)}")
        print(f"\nError connecting to Angus: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Communicate with Agent Angus via Coral Protocol')
    
    # Add arguments
    parser.add_argument('--server-url', type=str, 
                        default="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse",
                        help='Base URL of the Coral server (without query parameters)')
    parser.add_argument('--agent-id', type=str, default="yona",
                        help='ID to use for this agent')
    parser.add_argument('--wait-for-agents', type=int, default=2,
                        help='Number of agents to wait for')
    
    args = parser.parse_args()
    
    # Run the connection
    asyncio.run(connect_to_angus(
        args.server_url,
        args.agent_id,
        args.wait_for_agents
    ))

if __name__ == "__main__":
    main()
