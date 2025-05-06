# Coral Protocol LangChain Integration for Yona

This integration allows Yona to connect to a Coral Protocol server using LangChain's MCP module. It enables Yona to register its capabilities with the Coral server, discover other agents, and communicate with them through the Coral Protocol.

## Overview

The Coral Protocol is a standard for agent-to-agent communication that enables autonomous agents to discover each other and interact in a decentralized manner. This integration uses LangChain's implementation of the Coral Protocol to connect Yona to a Coral server.

The integration consists of:

1. `src/coral_langchain.py` - The main adapter class that connects Yona to a Coral server
2. `test_coral_langchain.py` - A test script to demonstrate the integration

## Requirements

- Python 3.10 or higher
- langchain-coral package
- A running Coral Protocol server

## Installation

1. Make sure you have Python 3.10 or higher installed
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Connecting to a Coral Server

```python
from src.agent import YonaAgent
from src.coral_langchain import YonaCoralAdapter

# Initialize Yona agent
yona_agent = YonaAgent()

# Initialize Coral adapter
coral_adapter = YonaCoralAdapter(
    yona_agent=yona_agent,
    coral_server_url="http://localhost:8000"
)

# Register with Coral server
success = coral_adapter.register_with_coral_server()
```

### Discovering Agents

```python
# Discover agents on the Coral server
agents = coral_adapter.discover_agents()

# Print discovered agents
for agent in agents:
    print(f"Agent: {agent.get('name')} ({agent.get('did')})")
```

### Getting Agent Capabilities

```python
# Get capabilities of an agent
agent_did = "did:web:example.com"
capabilities = coral_adapter.get_agent_capabilities(agent_did)
```

### Calling an Agent Function

```python
# Call a function on another agent
result = coral_adapter.call_agent(
    agent_did="did:web:example.com",
    function_name="create_song",
    prompt="Create a happy K-pop song about summer adventures"
)
```

### Starting a Coral Server

```python
# Start a server to listen for requests
coral_adapter.start_server(host="0.0.0.0", port=5001)
```

## Testing

You can use the `test_coral_langchain.py` script to test the integration:

```bash
# Test connection to a Coral server
python test_coral_langchain.py --server-url http://localhost:8000 --test connection

# Test getting agent capabilities
python test_coral_langchain.py --server-url http://localhost:8000 --test capabilities --agent-did did:web:example.com

# Test calling an agent function
python test_coral_langchain.py --server-url http://localhost:8000 --test call --agent-did did:web:example.com --function create_song --args '{"prompt": "Create a happy K-pop song about summer adventures"}'

# Start a Coral server
python test_coral_langchain.py --server-url http://localhost:8000 --test server --host 0.0.0.0 --port 5001
```

## Exposed Functions

The following functions are exposed through the Coral Protocol:

1. `create_song` - Create a song based on a prompt
2. `process_feedback` - Process feedback for a song
3. `list_songs` - List songs from the database

## Architecture

The integration uses the following components:

1. `YonaCoralAdapter` - The main adapter class that connects Yona to a Coral server
2. `CoralRunnable` - A LangChain component that exposes functions through the Coral Protocol
3. `CoralRunnableConfig` - Configuration for the CoralRunnable

The adapter uses the DID manager and capability document generator from the existing Yona MCP implementation to create a Coral Protocol identity and capability document.

## Future Improvements

- Add support for more Coral Protocol features
- Implement authentication and authorization
- Add more functions to expose through the Coral Protocol
- Improve error handling and logging
