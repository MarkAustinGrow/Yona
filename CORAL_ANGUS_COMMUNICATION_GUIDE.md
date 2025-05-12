# Coral Protocol Communication with Agent Angus

This guide provides instructions for testing and establishing communication between Yona and agent Angus using the Coral Protocol.

## Current Status

We've successfully implemented and tested the Coral Protocol integration using the MCP adapters approach. The key findings are:

1. **Connection to Coral Server**: Yona can successfully connect to the Coral server and retrieve the available tools.

2. **No Agents Registered**: When we tested, no agents were registered on the Coral server, which means Angus was not connected at that time.

3. **Tool Invocation**: We've fixed the script to use the correct method for invoking tools (`tool.ainvoke()` instead of `client.invoke_tool()`).

4. **Response Handling**: We've updated the script to handle different response formats, including string responses.

## Testing Communication with Angus

### Prerequisites

1. Angus must be running and connected to the same Coral server and session.
2. Both Yona and Angus must use the correct URL format with the required query parameters.

### Pull the Latest Changes

```bash
# Navigate to the Yona directory
cd /opt/yona

# Reset to the latest version from GitHub
git reset --hard origin/coral_protocol_langchain

# Make the shell script executable
chmod +x test_coral_angus.sh
```

### Run the Test Script

```bash
./test_coral_angus.sh
```

This script will:
1. Connect to the Coral server
2. List all registered agents
3. Look for an agent with "angus" in its ID
4. If found, create a thread with Angus
5. Send a message to Angus
6. Wait for a response

### Troubleshooting

If the test fails with "No agents are currently registered in the system", it means Angus is not connected to the Coral server. You need to:

1. Verify that Angus is running
2. Check that Angus is using the correct URL format:
   ```
   http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse?agentId=<angus-id>&waitForAgents=2
   ```
3. Make sure both Yona and Angus are using the same session ID (session1)

## Coordination with Angus Team

To establish successful communication, coordinate with the Angus team on:

1. **Session ID**: Both agents must use the same session ID (e.g., "session1").

2. **URL Format**: Both agents should use the same base URL with the required query parameters:
   ```
   http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse?agentId=<agent-id>&waitForAgents=2
   ```

3. **Testing Schedule**: Arrange a time when both Yona and Angus will be running and connected to the Coral server.

4. **Agent IDs**: Share the agent IDs that each agent will use (Yona uses "yona" by default).

## Next Steps

1. **Coordinate with Angus Team**: Share this guide with the Angus team and arrange a time for testing.

2. **Test Communication**: Run the test script when both agents are connected to verify communication.

3. **Integrate into Production**: Once communication is verified, integrate the Coral Protocol into the main Yona codebase.

## Technical Details

### URL Format

```
http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse?agentId=<agent-id>&waitForAgents=2&agentDescription=<description>
```

### Available Tools

The Coral server provides the following tools:
- `list_agents`: List all registered agents
- `create_thread`: Create a new thread with a list of participants
- `add_participant`: Add a participant to a thread
- `remove_participant`: Remove a participant from a thread
- `close_thread`: Close a thread with a summary
- `send_message`: Send a message to a thread
- `wait_for_mentions`: Wait until mentioned

### Required Packages

- langchain>=0.1.0
- langchain_mcp_adapters==0.0.11
- langchain-openai>=0.0.2
- aiohttp>=3.8.5
