# Coral Protocol Integration

This document provides an overview of the Coral Protocol integration with Yona, including recent fixes and improvements.

## Overview

The Coral Protocol enables AI agents to communicate with each other through a standardized messaging system. Yona is integrated with the Coral Protocol to allow other agents to request song creation.

## Recent Improvements

### 1. Fixed Agent ID

We've implemented a fixed agent ID (`yona-agent`) for Yona to ensure consistent identification across container restarts. This makes it easier for other agents to communicate with Yona.

**Changes made:**
- Updated `run_yona_coral.py` to use a fixed agent ID
- Modified `docker-compose.yml` to set the `YONA_SESSION_ID` environment variable
- Created `fix_coral_session_id.py` to diagnose and fix session ID issues

### 2. Improved Mention Detection

We've enhanced the mention detection logic in the Coral adapter to recognize various mention formats:

- Explicit mention in API call (`mentions=["yona-agent"]`)
- @mention in content (`@yona-agent`)
- <@mention> in content (`<@yona-agent>`)
- Name mention in content (`yona`)

**Changes made:**
- Created `improved_fix_coral_adapter.py` to update the mention detection logic
- Added more detailed logging to help diagnose issues
- Implemented checks for various mention formats

### 3. Testing Tools

We've created several tools to test the Coral Protocol integration:

- `test_mention_formats.py`: Tests different mention formats to see which ones work
- `agent_angus.py`: A sample agent implementation that communicates with Yona

## Usage

### Running Yona with Coral Protocol

1. Start the Yona container with Coral Protocol support:
   ```bash
   docker-compose up -d yona-coral
   ```

2. Check the logs to verify that Yona is connected to the Coral server:
   ```bash
   docker logs yona_yona-coral_1
   ```

   Look for messages like:
   ```
   INFO:yona_coral:Creating Coral adapter with session ID: yona-agent
   INFO:coral_client:Initialized Coral client with session ID: yona-agent
   INFO:src.coral_adapter:YonaCoralAdapter initialized with session ID: yona-agent
   ```

### Testing with Agent Angus

1. Install the required dependencies:
   ```bash
   pip install coral-client
   ```

2. Run Agent Angus with a song topic:
   ```bash
   python agent_angus.py --topic "artificial intelligence and creativity" --verbose
   ```

3. Agent Angus will:
   - Register with the Coral server
   - Create a thread with Yona
   - Send a message requesting a song
   - Listen for responses from Yona

4. Check the logs to see the communication between Angus and Yona:
   ```bash
   # In one terminal, watch Angus logs
   # (They'll be printed to the console)

   # In another terminal, watch Yona logs
   docker logs -f yona_yona-coral_1
   ```

## Troubleshooting

### Common Issues

1. **No response from Yona**:
   - Ensure Yona is running with the correct session ID
   - Check if the Coral server is operational
   - Verify that the mention formats are correct

2. **Connection issues**:
   - The SSE connection may time out after 60 seconds; the client should automatically reconnect
   - Verify your network connection to the Coral server

3. **Message not detected as a mention**:
   - Include the agent ID in the `mentions` list
   - Use the `@yona-agent` format in the message content
   - Include the word "yona" in your message

### Diagnostic Commands

1. Check if Yona is running:
   ```bash
   docker ps | grep yona-coral
   ```

2. Check Yona's logs:
   ```bash
   docker logs yona_yona-coral_1
   ```

3. Check for mention detection:
   ```bash
   docker logs yona_yona-coral_1 | grep -E "Found mention|Received message mention"
   ```

4. Check for errors:
   ```bash
   docker logs yona_yona-coral_1 | grep ERROR
   ```

## Documentation

For more detailed information, refer to the following documents:

- [AGENT_COMMUNICATION_GUIDE.md](AGENT_COMMUNICATION_GUIDE.md): Comprehensive guide for agent-to-agent communication
- [CORAL_FIXED_AGENT_ID.md](CORAL_FIXED_AGENT_ID.md): Details about the fixed agent ID implementation
- [CORAL_MENTION_DETECTION_FIX.md](CORAL_MENTION_DETECTION_FIX.md): Information about the mention detection improvements
- [CORAL_SESSION_ID_FIX.md](CORAL_SESSION_ID_FIX.md): Guide for fixing session ID issues

## Future Improvements

1. **Enhanced Error Handling**: Improve error handling and recovery mechanisms
2. **Message Queuing**: Implement a message queue to handle high volumes of requests
3. **Agent Discovery**: Add support for discovering other agents on the Coral server
4. **Authentication**: Implement authentication for secure agent-to-agent communication
