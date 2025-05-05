# Simple Coral Agent

A lightweight Python client for connecting to the Coral server and communicating with the Yona agent without requiring DID capabilities.

## Overview

This package provides a simple way to connect to the Coral server and communicate with the Yona agent. It includes:

- A simplified Coral client (`simple_coral_agent.py`)
- A test script to demonstrate usage (`test_coral_communication.py`)
- A comprehensive guide (`SIMPLE_CORAL_AGENT_GUIDE.md`)
- A requirements file (`simple_coral_agent_requirements.txt`)

## Key Features

- **JSON-RPC Format Support**: Properly formats messages with the required "id" field to comply with the Coral server's JSON-RPC expectations
- **SSE Connection Handling**: Establishes and maintains a Server-Sent Events connection to the Coral server
- **Session ID Extraction**: Automatically extracts the session ID from the endpoint event
- **Thread-Safe Queue**: Uses a thread-safe queue for message processing

## Quick Start

1. Install the required dependencies:

```bash
pip install -r simple_coral_agent_requirements.txt
```

2. Run the test script:

```bash
python test_coral_communication.py
```

This will:
- Connect to the Coral server
- Register a test agent
- Create a thread with the Yona agent
- Send a test message
- Wait for and process any responses

## Documentation

For detailed instructions on how to use the Simple Coral Agent, please refer to the [SIMPLE_CORAL_AGENT_GUIDE.md](SIMPLE_CORAL_AGENT_GUIDE.md) file.

## Files

- `simple_coral_agent.py`: The main client class for connecting to the Coral server
- `test_coral_communication.py`: A test script demonstrating how to use the client
- `SIMPLE_CORAL_AGENT_GUIDE.md`: A comprehensive guide to using the client
- `simple_coral_agent_requirements.txt`: A list of required dependencies

## Requirements

- Python 3.7 or higher
- requests
- sseclient-py
- httpx (optional)

## License

This project is open source and available under the MIT License.
