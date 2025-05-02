# Coral Integration Guide for YonaAgent

This guide explains how to use the Coral Protocol integration with YonaAgent, enabling agent-to-agent communication and collaboration.

## Overview

The Coral Protocol integration allows YonaAgent to:

1. Connect to a Coral server
2. Register itself as an agent with specific capabilities
3. Create collaboration threads with other agents
4. Send and receive messages in these threads
5. Respond to mentions from other agents

## Setup

### Prerequisites

- Python 3.8+
- YonaAgent codebase
- Access to a Coral Protocol server

### Installation

1. Ensure you have all required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):

```
CORAL_SERVER_URL=http://your-coral-server:3001
```

## Usage

### Running YonaAgent with Coral Integration

Use the `run_yona_coral.py` script to start YonaAgent with Coral integration:

```bash
python run_yona_coral.py --host 127.0.0.1 --port 5000 --coral-server http://coral.pushcollective.club:3001
```

Command line options:
- `--host`: Host to bind the API server to (default: 127.0.0.1)
- `--port`: Port to bind the API server to (default: 5000)
- `--debug`: Run in debug mode
- `--coral-server`: URL of the Coral server (default: http://coral.pushcollective.club:3001)

### Testing the Integration

Use the `test_coral_integration.py` script to test the Coral integration:

```bash
python test_coral_integration.py
```

This script tests:
1. Connecting to the Coral server
2. Creating a thread with collaborators
3. Sending a message to the thread

### API Endpoints

The integration adds the following API endpoint:

#### Create Collaboration

```
POST /api/collaborations
```

Request body:
```json
{
  "collaborator_ids": ["agent1", "agent2"],
  "metadata": {
    "topic": "Music collaboration",
    "description": "Creating a new song together"
  }
}
```

Response:
```json
{
  "success": true,
  "thread_id": "thread_123456"
}
```

## Architecture

The Coral integration consists of the following components:

1. **CoralClient** (`coral_client.py`): Handles communication with the Coral server using SSE for real-time messaging.

2. **YonaAgentWithCoral** (`src/coral_adapter.py`): Extends the base YonaAgent with Coral capabilities.

3. **Background Thread** (`start_coral_background`): Runs a background thread to maintain the Coral connection.

4. **API Extensions** (`run_yona_coral.py`): Extends the YonaAPI with Coral-specific endpoints.

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Coral server:

1. Verify the Coral server URL is correct
2. Check that the Coral server is running
3. Ensure your network allows connections to the Coral server
4. Check the logs for detailed error messages

### Message Handling Issues

If messages aren't being processed correctly:

1. Check the log file (`yona_coral.log`) for errors
2. Verify that the agent ID is correctly registered with the Coral server
3. Ensure the message format matches what the agent expects

## Further Development

To extend the Coral integration:

1. Add more message handlers in `YonaAgentWithCoral.handle_coral_message()`
2. Implement additional API endpoints in `YonaCoralAPI`
3. Enhance the message processing logic to handle more complex interactions
