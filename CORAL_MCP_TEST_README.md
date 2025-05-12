# Testing Communication with Agent Angus via Coral Protocol

This README provides instructions for testing communication between Yona and Agent Angus using the Coral Protocol with the MCP adapters approach.

## Background

Based on our investigation, we found that both Yona and Angus were trying to use direct HTTP endpoints for discovery and communication, while the Coral server expects them to use MCP tools provided through the SSE connection. This is why both agents were encountering 404 errors when trying to discover each other.

The `test_coral_mcp.py` script implements the correct approach using the `langchain_mcp_adapters` package, which aligns with the Coral server's expectations.

## Prerequisites

The following Python packages are required:
- langchain
- langchain_mcp_adapters
- langchain-openai

## Installation

### Option 1: Install on the Server

```bash
pip install langchain langchain_mcp_adapters langchain-openai
```

### Option 2: Install in the Docker Container

```bash
docker exec -it 59ff25c1a6a5 pip install langchain langchain_mcp_adapters langchain-openai
```

## Running the Test

### Option 1: Run on the Server

```bash
python test_coral_mcp.py
```

### Option 2: Run in the Docker Container

```bash
docker cp test_coral_mcp.py 59ff25c1a6a5:/app/
docker exec -it 59ff25c1a6a5 python /app/test_coral_mcp.py
```

## Command-Line Options

The script supports the following command-line options:

- `--server-url`: Base URL of the Coral server (default: "http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse")
- `--agent-id`: ID to use for this agent (default: "yona")
- `--wait-for-agents`: Number of agents to wait for (default: 2)

Example with custom options:

```bash
python test_coral_mcp.py --agent-id "yona_test" --wait-for-agents 3
```

## What the Script Does

1. Connects to the Coral server using the SSE endpoint with the correct query parameters
2. Gets the available tools from the server
3. Lists all registered agents using the `list_agents` tool
4. Looks for an agent with "angus" in its ID
5. If Angus is found:
   - Creates a thread with Angus
   - Sends a message to Angus
   - Waits for a response
6. Prints the results of each step

## Interpreting the Results

- If the script runs successfully and finds Angus, it will create a thread and send a message
- If Angus responds, you'll see the response in the "Received mentions" output
- If the script fails with an ImportError, you need to install the required packages
- If the script fails with other errors, check the error message for details

## Troubleshooting

- **ImportError**: Install the required packages as described above
- **Connection Error**: Verify that the Coral server is running and accessible
- **No Agents Found**: Verify that Angus is connected to the same Coral server and session
- **Angus Not Found**: Verify that Angus's agent ID contains "angus" (case-insensitive)
- **No Response from Angus**: Verify that Angus is properly handling mentions and sending responses

## Next Steps

If the test is successful, you can:

1. Update the core Yona implementation to use this approach
2. Implement more sophisticated communication patterns
3. Integrate this functionality into the main Yona API

If the test fails, you can:

1. Check the error messages for clues
2. Verify that Angus is using the same approach
3. Contact the Coral server team for assistance
