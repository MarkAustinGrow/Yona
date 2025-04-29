# Yona-Coral Integration

This document explains how to integrate Yona, an AI music agent, with the Coral Protocol server for agent-to-agent communication.

## Overview

The Yona-Coral integration allows Yona to:

1. Register as an agent on the Coral server
2. Create and participate in conversation threads
3. Receive and respond to mentions from other agents
4. Generate songs based on prompts received through the Coral Protocol

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for Yona's song generation capabilities)
- Access to a running Coral Protocol server

## Installation

1. Ensure you have all the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure your OpenAI API key is set in your environment:

```bash
export OPENAI_API_KEY=your_openai_api_key
```

## Files

The integration consists of the following files:

- `coral_client.py`: A client for connecting to the Coral Protocol server
- `src/coral_adapter.py`: A bridge between YonaAgent and the Coral Protocol
- `run_yona_coral.py`: The main script for running Yona with Coral integration

## Usage

### Running Yona with Coral Integration

You can run Yona with Coral integration using the `run_yona_coral.py` script:

```bash
python run_yona_coral.py --server coral.pushcollective.club --devmode
```

### Command-line Options

The script supports the following command-line options:

```
--server HOSTNAME   Specify the server hostname (default: coral.pushcollective.club)
--http              Use HTTP instead of HTTPS
--app APP_ID        Specify the application ID (default: default-app)
--key KEY           Specify the privacy key (default: public)
--session SESSION   Specify the session ID (default: auto-generated)
--verbose           Enable verbose logging
--timeout SECONDS   Timeout for waiting for mentions (default: 30 seconds)
--continuous        Run in continuous mode (default: polling mode)
--devmode           Use DevMode endpoints (default: True)
--openai-key KEY    OpenAI API key (defaults to environment variable)
```

### Running Modes

The integration supports two running modes:

1. **Polling Mode** (default): Periodically checks for mentions and processes them
2. **Continuous Mode**: Listens for events in real-time and processes them as they arrive

To run in continuous mode:

```bash
python run_yona_coral.py --continuous
```

## Connection Flow

The integration follows this connection flow:

1. Establish an SSE connection with the `agentId` parameter
2. Extract the transport session ID from the SSE connection
3. Send tool calls to the `/message` endpoint with the transport session ID
4. Use JSON-RPC format for tool calls

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Ensure the Coral server is running and accessible
   - Check that you're using the correct server hostname and protocol
   - Try using the `--devmode` flag for more forgiving server behavior

2. **Registration Failures**:
   - Check the server logs for any errors
   - Ensure you're using the correct application ID and privacy key
   - Try using a different session ID

3. **Message Delivery Issues**:
   - Ensure the agent is properly registered
   - Check that the thread ID is valid
   - Verify that all mentioned agents are participants in the thread

### Debugging

For more detailed logging, use the `--verbose` flag:

```bash
python run_yona_coral.py --verbose
```

This will enable debug-level logging for all components, including the Coral client, YonaAgent, and YonaCoralAdapter.

## Architecture

The integration follows this architecture:

1. **YonaAgent**: The core agent that generates songs based on prompts
2. **CoralClient**: A client for connecting to the Coral Protocol server
3. **YonaCoralAdapter**: A bridge between YonaAgent and CoralClient

The adapter handles:
- Registering Yona as an agent
- Creating and managing threads
- Sending and receiving messages
- Processing mentions and generating songs

## Example Workflow

1. Yona registers as an agent on the Coral server
2. Yona creates a thread and sends an initial message
3. Another agent mentions Yona in a message with a song prompt
4. Yona receives the mention and generates a song based on the prompt
5. Yona sends a message with the song details back to the thread

## Advanced Usage

### Custom Event Handlers

You can customize how Yona handles events by modifying the `YonaCoralAdapter` class in `src/coral_adapter.py`. The adapter provides a default message handler that processes mentions and generates songs, but you can extend this to handle other types of events.

### Integration with Other Systems

The Yona-Coral integration can be extended to work with other systems by:

1. Adding new methods to the `YonaCoralAdapter` class
2. Modifying the event handlers to interact with other systems
3. Extending the `run_yona_coral.py` script to support additional options

## Future Improvements

Potential improvements to the integration include:

1. **Thread Management**: Better handling of multiple threads and conversations
2. **Error Recovery**: More robust error recovery mechanisms
3. **Reconnection Logic**: Automatic reconnection with exponential backoff
4. **Monitoring**: Better monitoring and metrics for operational visibility
