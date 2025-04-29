# Coral Protocol Agent Communication

This document explains the integration between Yona and other agents via the Coral Protocol, focusing on the communication between Yona (music creation agent) and a YouTube agent.

## Overview

The Coral Protocol enables different AI agents to communicate with each other through a standardized messaging system. This integration allows Yona to interact with other specialized agents, creating powerful workflows that combine their capabilities.

### Current Integration

- **Yona Agent**: Creates original songs based on prompts or requests
- **YouTube Agent**: Analyzes YouTube videos to extract song descriptions and uploads videos to a specific channel

## Benefits of Agent-to-Agent Communication

1. **Specialized Capabilities**: Each agent can focus on what it does best
2. **Workflow Automation**: Complex tasks can be broken down and distributed across agents
3. **Enhanced Creativity**: Agents can build on each other's outputs
4. **Scalability**: New agents can be added to extend functionality without modifying existing agents
5. **User Experience**: End users can interact with a network of agents through a single interface

## Example Workflows

### Workflow 1: Song Creation → YouTube Upload
1. A user requests Yona to create a song
2. Yona generates the song
3. The YouTube agent uploads the song to YouTube
4. The YouTube agent returns the link to the uploaded video

### Workflow 2: YouTube Analysis → Inspiration → New Song
1. The YouTube agent analyzes an existing song on YouTube
2. It provides a description of the song to Yona
3. Yona creates a new song inspired by the analyzed song
4. The YouTube agent uploads the new song

## Technical Implementation

The integration uses the Coral Protocol client library to:

1. Register agents with the Coral server
2. Create threads for conversations
3. Send messages with mentions to specific agents
4. Listen for mentions and respond accordingly

### Key Components

- `coral_client.py`: Client library for interacting with the Coral Protocol server
- `src/coral_adapter.py`: Adapter that integrates Yona with the Coral Protocol
- `run_yona_coral.py`: Script to run Yona as a Coral agent

## Testing the Integration

We've created two scripts to test and demonstrate the agent communication:

### 1. Basic Communication Test

The `test_agent_communication.py` script tests basic communication between Yona and the YouTube agent:

```bash
python test_agent_communication.py --yona-agent-id yona-agent-1745921981 --youtube-agent-id youtube-agent
```

This script:
- Creates a thread with both agents
- Has the YouTube agent request a song from Yona
- Waits for a response
- Reports whether communication was successful

### 2. Complete Workflow Simulation

The `simulate_agent_workflow.py` script simulates a complete workflow between the agents:

```bash
python simulate_agent_workflow.py --yona-agent-id yona-agent-1745921981 --youtube-agent-id youtube-agent --simulate-responses
```

This script:
- Creates a thread with both agents
- Has the YouTube agent request a song from Yona
- Monitors for Yona's response with a song
- Has the YouTube agent respond with analysis and upload confirmation
- Can simulate responses if agents don't respond (with `--simulate-responses`)

## Configuration

Both test scripts accept the following command-line arguments:

- `--yona-agent-id`: ID of the Yona agent (default: "yona-agent")
- `--youtube-agent-id`: ID of the YouTube agent (default: "youtube-agent")
- `--server-url`: URL of the Coral server (default: "https://coral.pushcollective.club")
- `--session-id`: Session ID for the test (default: generated based on timestamp)

The workflow simulation script also accepts:

- `--poll-interval`: How often to check for new messages (seconds, default: 10)
- `--max-wait-time`: Maximum time to wait for workflow completion (seconds, default: 300)
- `--simulate-responses`: Flag to simulate responses if agents don't respond

## Monitoring and Debugging

To monitor the Coral integration, you can:

1. Check the logs of the Yona Coral container:
   ```bash
   docker-compose logs -f yona-coral
   ```

2. Run the test scripts with detailed logging:
   ```bash
   python test_agent_communication.py --yona-agent-id yona-agent-1745921981 --youtube-agent-id youtube-agent
   ```

3. Use the Coral server's admin interface (if available) to view threads and messages

## Troubleshooting

### Common Issues

1. **Agent Not Responding to Mentions**:
   - Check if the agent is properly connected to the Coral server
   - Verify that the agent ID in the mention matches the registered agent ID
   - Ensure the agent is properly listening for mentions

2. **Connection Issues**:
   - Verify the Coral server URL is correct
   - Check network connectivity
   - Ensure the server is running and accessible

3. **Message Delivery Problems**:
   - Check if the thread exists and both agents are participants
   - Verify that the message format is correct
   - Check for any rate limiting or permission issues

## Future Enhancements

1. **Additional Agents**: Integrate with more specialized agents (e.g., image generation, text analysis)
2. **Enhanced Workflows**: Create more complex workflows involving multiple agents
3. **User Interface**: Develop a UI for users to interact with the agent network
4. **Analytics**: Track and analyze agent interactions to improve performance

## References

- [Coral Protocol Documentation](https://coral.pushcollective.club/docs)
- [Yona Documentation](https://github.com/MarkAustinGrow/Yona)
