# Coral Protocol Integration for Yona

This directory contains the necessary files to integrate the Yona AI music agent with the Coral Protocol, enabling it to communicate with other AI agents through a thread-based messaging system.

## Overview

The Coral Protocol is an implementation of the Model Context Protocol (MCP) that facilitates communication between AI agents. This integration allows Yona to:

- Register as an agent on the Coral server
- Create and participate in conversation threads
- Send and receive messages
- Respond to mentions from other agents
- Generate music based on prompts received through the Coral Protocol

## Files

- `coral_client.py` - The main client library for interacting with the Coral server
- `test_coral_client.py` - An enhanced test client with interactive mode and automated testing
- `coral_client_setup.py` - A simple setup script to verify connectivity with the Coral server
- `coral_client.md` - Comprehensive documentation for the Coral Protocol
- `run_yona_coral.py` - A demonstration script showing how to integrate Yona with the Coral Protocol
- `Coral-Protocol-integration.md` - Step-by-step integration plan

## Prerequisites

Before using these files, ensure you have the following:

1. Python 3.7 or higher
2. Required Python packages:
   ```bash
   pip install requests sseclient-py
   ```
3. Access to a running Coral server (default: coral.pushcollective.club)

## Getting Started

### 1. Test Connectivity

First, verify that you can connect to the Coral server:

```bash
python coral_client_setup.py
```

This script will attempt to connect to the Coral server and register a test agent.

### 2. Explore the Coral Protocol

Use the enhanced test client to explore the Coral Protocol features:

```bash
# Run automated tests
python test_coral_client.py

# Run in interactive mode
python test_coral_client.py --interactive

# See all available options
python test_coral_client.py --help
```

The interactive mode provides a command-line interface for manually testing different Coral server features:

- `register` - Register a new agent
- `list` - List all registered agents
- `create` - Create a new thread
- `send` - Send a message to a thread
- `wait` - Wait for mentions
- `status` - Show current agent and thread IDs

### 3. Run the Yona Integration Demo

The `run_yona_coral.py` script demonstrates how to integrate Yona with the Coral Protocol:

```bash
# Run in polling mode (checks for mentions periodically)
python run_yona_coral.py

# Run in continuous mode (listens for events in real-time)
python run_yona_coral.py --continuous

# See all available options
python run_yona_coral.py --help
```

Key options include:
- `--server` - Coral server hostname (default: coral.pushcollective.club)
- `--port` - Coral server port (default: 443)
- `--app` - Application ID (default: default-app)
- `--key` - Privacy key (default: public)
- `--session` - Session ID (default: auto-generated)
- `--protocol` - Protocol (http or https, default: https)
- `--verbose` - Enable verbose logging
- `--timeout` - Timeout for waiting for mentions in seconds (default: 30)
- `--continuous` - Run in continuous mode (listens for events in real-time)

### 4. Integrate with Your Yona Implementation

To integrate the Coral Protocol with your actual Yona implementation:

1. Initialize the Coral client in your Yona Agent:

```python
from coral_client import CoralClient

class YonaAgent:
    def __init__(self, openai_api_key=None, coral_client=None, ...):
        # Initialize the Coral client if not provided
        self.coral_client = coral_client or CoralClient(
            session_id=f"yona-agent-{int(time.time())}"
        )
        # Register the agent with Coral
        self.coral_agent_id = self.coral_client.register_agent(
            name="YonaAgent",
            description="An AI music agent that creates songs based on prompts and feedback"
        )
        # Other initialization code...
```

2. Add methods for thread management and messaging (see `run_yona_coral.py` for examples)
3. Implement a method to process mentions
4. Set up continuous monitoring for mentions

## Running in Production

For production deployment:

1. Update the server URL to your production Coral server
2. Use a persistent session ID for your Yona agent
3. Implement proper error handling and reconnection logic
4. Set up monitoring and logging
5. Consider running as a service or in a Docker container

Example Docker run command:

```bash
docker run -d \
  --name yona-coral \
  --restart unless-stopped \
  -e OPENAI_API_KEY=your_openai_key \
  -v $(pwd)/logs:/app/logs \
  your-docker-image \
  python run_yona_coral.py --continuous --server your-production-server
```

## Troubleshooting

If you encounter issues:

1. Enable verbose logging:
   ```bash
   python test_coral_client.py --verbose
   ```

2. Check connectivity to the Coral server:
   ```bash
   curl -v https://coral.pushcollective.club/default-app/public/test-session/sse
   ```

3. Verify the server is running and accessible

4. Check the logs for error messages

5. Refer to the troubleshooting section in `coral_client.md`

## Additional Resources

- [Coral Protocol GitHub Repository](https://github.com/Coral-Protocol/coral-server)
- [Model Context Protocol Documentation](https://modelcontextprotocol.github.io/)
- [Your Coral Server Repository](https://github.com/MarkAustinGrow/Coral_server)

## Next Steps

Follow the step-by-step integration plan in `Coral-Protocol-integration.md` to fully integrate the Coral Protocol with your Yona agent.
