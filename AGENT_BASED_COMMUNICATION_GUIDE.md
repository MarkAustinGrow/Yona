# Agent-Based Communication with Angus via Coral Protocol

This guide explains how to use the agent-based approach to communicate with Agent Angus via the Coral Protocol server.

## Overview

Based on feedback from Team Angus, we've implemented a new approach for communicating with Angus via the Coral Protocol server. This approach uses LangChain's agent framework to create an agent that can interact with the Coral Protocol tools.

## Key Components

1. **agent_angus_communication.py**: Main script that connects to the Coral server and creates an agent
2. **run_agent_angus_communication.sh** / **run_agent_angus_communication.bat**: Shell/batch scripts to run the main script in the Docker container
3. **agent_requirements.txt**: Requirements file with the specific package versions needed

## Important Notes

1. **Package Versions**: We're using `langchain_mcp_adapters==0.0.10` as recommended by Team Angus. Newer versions may have API incompatibilities.

2. **Agent ID**: Team Angus is using "angus_agent" as their agent ID. We're using "yona" as our agent ID.

3. **Server URL**: We're using the same server URL as Team Angus:
   ```
   http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse
   ```

4. **OpenAI API Key**: The script requires an OpenAI API key to create the agent. The key should be in the `.env` file in the Docker container with the variable name `OPENAI_KEY` or `OPENAI_API_KEY`. The script will automatically load it using `python-dotenv`.

5. **Agent Approach**: Instead of directly invoking tools, we're creating an agent with the tools and letting the agent invoke them.

## How It Works

1. The script connects to the Coral Protocol server using the specified URL and agent ID.
2. It retrieves the available tools from the server.
3. It creates a LangChain agent with those tools.
4. The agent is given instructions to:
   - List all registered agents
   - Look for an agent with "angus" in its ID or description
   - Create a thread with that agent
   - Send a message introducing itself
   - Wait for a response

## Running the Script

### On Linux/macOS

```bash
# Make the script executable
chmod +x run_agent_angus_communication.sh

# Run the script with default parameters
./run_agent_angus_communication.sh

# Or with custom parameters
./run_agent_angus_communication.sh --container-id <container-id> --agent-id <agent-id> --wait-for-agents <number>
```

### On Windows

```batch
# Run the script with default parameters
run_agent_angus_communication.bat

# Or with custom parameters
run_agent_angus_communication.bat --container-id <container-id> --agent-id <agent-id> --wait-for-agents <number>
```

## Command Line Options

- `--container-id`: Docker container ID (default: 59ff25c1a6a5)
- `--agent-id`: ID to use for this agent (default: yona)
- `--wait-for-agents`: Number of agents to wait for (default: 2)
- `--server-url`: Coral server URL (default: http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse)

## Coordination with Team Angus

For successful communication, both Yona and Angus need to be connected to the Coral server at the same time. Coordinate with Team Angus to arrange a specific time for testing.

## Troubleshooting

1. **No Agents Found**: If the script reports "No agents are currently registered in the system", it means Angus is not connected to the server. Coordinate with Team Angus to ensure they're connected at the same time.

2. **Package Version Issues**: If you encounter errors related to package versions, make sure you're using the correct versions:
   - langchain-core>=0.3.36,<0.4.0
   - langchain_mcp_adapters==0.0.10
   - langchain-openai>=0.0.2
   - python-dotenv>=0.21.0

3. **OpenAI API Key Issues**: If you see an error like "Neither OPENAI_KEY nor OPENAI_API_KEY environment variables are set", make sure the `.env` file in the Docker container contains the OpenAI API key with the variable name `OPENAI_KEY` or `OPENAI_API_KEY`. You can copy the `.env` file to the container with:
   ```bash
   docker cp .env <container-id>:/app/
   ```

4. **Connection Issues**: If you can't connect to the server, check that the server URL is correct and that you have internet access.

## Next Steps

1. Coordinate with Team Angus to arrange a time for testing.
2. Run the script when both agents are connected.
3. Verify that the agents can communicate with each other.
4. Integrate the agent-based approach into the main Yona codebase.
