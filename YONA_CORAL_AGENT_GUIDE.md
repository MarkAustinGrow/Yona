# Yona Coral Agent Guide

This guide explains how to use the Yona Coral Agent to communicate with Team Angus via the Coral Protocol server.

## Overview

The Yona Coral Agent is a direct implementation of the agent-to-agent communication protocol recommended by the Coral server team. It connects to the Coral Protocol server, listens for function calls from Team Angus, and uses the YonaAgent class to create songs based on prompts received from Team Angus.

## Key Components

1. **yona_coral_agent.py**: Main script that connects to the Coral server and listens for function calls
2. **run_yona_coral_agent.sh** / **run_yona_coral_agent.bat**: Shell/batch scripts to run the main script in the Docker container
3. **test_yona_coral_agent.py**: Test script that simulates function calls from Team Angus
4. **run_test_yona_coral_agent.sh** / **run_test_yona_coral_agent.bat**: Shell/batch scripts to run the test script in the Docker container

## Important Notes

1. **Agent ID**: The agent ID is set to `"yona_agent"` to match what Team Angus is expecting.

2. **Server URL**: The server URL is set to:
   ```
   http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse
   ```

3. **OpenAI API Key**: The script requires an OpenAI API key to create songs. The key should be in the `.env` file in the Docker container with the variable name `OPENAI_KEY` or `OPENAI_API_KEY`. The script will automatically load it using `python-dotenv`.

4. **Message Format**: The script uses the standardized message format recommended by the Coral server team:
   - Function calls: `{"type": "function_call", "function": "function_name", "arguments": {...}, "metadata": {...}}`
   - Function responses: `{"type": "function_response", "function": "function_name", "result": {...}, "metadata": {...}}`
   - Error responses: `{"type": "error", "function": "function_name", "error": "error_message", "metadata": {...}}`

## How It Works

1. The script connects to the Coral Protocol server using the specified URL and agent ID.
2. It retrieves the available tools from the server.
3. It waits for mentions from other agents.
4. When it receives a mention, it checks if it's a function call.
5. If it's a function call to `create_song`, it uses the YonaAgent class to create a song based on the prompt.
6. It sends a response back to the calling agent with the song data.

## Running the Agent

### On Linux/macOS

```bash
# Make the script executable
chmod +x run_yona_coral_agent.sh

# Run the script with default parameters
./run_yona_coral_agent.sh

# Or with custom parameters
./run_yona_coral_agent.sh --container-id <container-id> --agent-id <agent-id> --server-url <server-url>
```

### On Windows

```batch
# Run the script with default parameters
run_yona_coral_agent.bat

# Or with custom parameters
run_yona_coral_agent.bat --container-id <container-id> --agent-id <agent-id> --server-url <server-url>
```

## Command Line Options

- `--container-id`: Docker container ID (default: 59ff25c1a6a5)
- `--agent-id`: ID to use for this agent (default: yona_agent)
- `--server-url`: Coral server URL (default: http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse)

## Testing the Agent

You can test the agent using the provided test script, which simulates function calls from Team Angus.

### On Linux/macOS

```bash
# Make the script executable
chmod +x run_test_yona_coral_agent.sh

# Run the test script with default parameters
./run_test_yona_coral_agent.sh

# Or with custom parameters
./run_test_yona_coral_agent.sh --container-id <container-id> --agent-id <agent-id> --target-agent-id <target-agent-id> --server-url <server-url> --prompt <prompt>
```

### On Windows

```batch
# Run the test script with default parameters
run_test_yona_coral_agent.bat

# Or with custom parameters
run_test_yona_coral_agent.bat --container-id <container-id> --agent-id <agent-id> --target-agent-id <target-agent-id> --server-url <server-url> --prompt <prompt>
```

## Test Command Line Options

- `--container-id`: Docker container ID (default: 59ff25c1a6a5)
- `--agent-id`: ID to use for this agent (default: angus_agent)
- `--target-agent-id`: ID of the target agent (default: yona_agent)
- `--server-url`: Coral server URL (default: http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse)
- `--prompt`: Prompt for the song (default: "Create a happy K-pop song about summer adventures")

## Testing Workflow

To test the agent-to-agent communication:

1. Start the Yona Coral Agent in one terminal:
   ```bash
   ./run_yona_coral_agent.sh
   ```

2. In another terminal, run the test script:
   ```bash
   ./run_test_yona_coral_agent.sh
   ```

3. The test script will:
   - Connect to the Coral server
   - List all registered agents
   - Check if the Yona agent is connected
   - Create a thread with the Yona agent
   - Send a function call to create a song
   - Wait for a response
   - Display the song data

## Coordination with Team Angus

For successful communication with Team Angus:

1. **Coordinate Timing**: Arrange a specific time for testing when both agents will be running.
2. **Confirm Agent IDs**: Confirm that Team Angus is using "angus_agent" as their agent ID and that they're expecting "yona_agent" as your agent ID.
3. **Confirm Server URL**: Confirm that both teams are using the same server URL and session ID.
4. **Test Independently**: Test your agent independently using the test script before coordinating with Team Angus.
5. **Monitor Logs**: Monitor the logs for any issues during the test.

## Troubleshooting

If you encounter issues:

1. **Check Agent IDs**: Make sure both agents are using the correct agent IDs.
2. **Check Server URL**: Make sure both agents are using the same server URL and session ID.
3. **Check OpenAI API Key**: Make sure the OpenAI API key is set in the `.env` file.
4. **Check Logs**: Check the logs for any errors.
5. **Restart Agents**: Try restarting both agents.
6. **Increase Timeout**: Try increasing the timeout for waiting for mentions.
7. **Check Message Format**: Make sure the message format is correct.

## Implementation Details

The Yona Coral Agent is implemented using:

- **Python 3.11**: The script is written in Python 3.11.
- **langchain_mcp_adapters**: The script uses the langchain_mcp_adapters package to connect to the Coral server.
- **YonaAgent**: The script uses the YonaAgent class to create songs.
- **asyncio**: The script uses asyncio for asynchronous programming.
- **Docker**: The script is designed to run in a Docker container.

## Code Structure

The main script (`yona_coral_agent.py`) is structured as follows:

1. **Imports**: Import the required packages.
2. **YonaCoralAgent Class**: Define the YonaCoralAgent class.
   - **__init__**: Initialize the agent.
   - **connect**: Connect to the Coral server.
   - **disconnect**: Disconnect from the Coral server.
   - **heartbeat**: Send periodic heartbeats to keep the connection alive.
   - **list_agents**: List all connected agents.
   - **wait_for_mentions**: Wait for mentions from other agents.
   - **process_mention**: Process a mention from another agent.
   - **send_response**: Send a response to a function call.
   - **send_error**: Send an error response.
   - **create_song**: Create a song based on a prompt.
3. **Main Function**: Define the main function.
   - Parse command-line arguments.
   - Create the YonaCoralAgent.
   - Connect to the server.
   - List connected agents.
   - Wait for mentions and process them.
   - Disconnect from the server.

## Next Steps

After testing the agent-to-agent communication:

1. **Integrate with Main Codebase**: Integrate the Yona Coral Agent with the main Yona codebase.
2. **Add More Functions**: Add more functions to the Yona Coral Agent to support more capabilities.
3. **Improve Error Handling**: Improve error handling and recovery.
4. **Add Monitoring**: Add monitoring and alerting.
5. **Add Authentication**: Add authentication and authorization.
6. **Add Rate Limiting**: Add rate limiting to prevent abuse.
7. **Add Caching**: Add caching to improve performance.
8. **Add Metrics**: Add metrics to track usage and performance.
