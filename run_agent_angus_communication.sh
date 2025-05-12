#!/bin/bash
# Script to run the agent_angus_communication.py script in the Docker container

# Set default values
CONTAINER_ID="59ff25c1a6a5"  # Default container ID for yona_yona-api_1
AGENT_ID="yona"
WAIT_FOR_AGENTS=2
SERVER_URL="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --container-id)
      CONTAINER_ID="$2"
      shift 2
      ;;
    --agent-id)
      AGENT_ID="$2"
      shift 2
      ;;
    --wait-for-agents)
      WAIT_FOR_AGENTS="$2"
      shift 2
      ;;
    --server-url)
      SERVER_URL="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container-id ID      Docker container ID (default: 59ff25c1a6a5)"
      echo "  --agent-id ID          Agent ID to use (default: yona)"
      echo "  --wait-for-agents N    Number of agents to wait for (default: 2)"
      echo "  --server-url URL       Coral server URL (default: http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse)"
      echo "  --help                 Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo "=== Running Agent-Based Communication with Angus via Coral Protocol ==="
echo "Container ID: $CONTAINER_ID"
echo "Agent ID: $AGENT_ID"
echo "Wait for agents: $WAIT_FOR_AGENTS"
echo "Server URL: $SERVER_URL"
echo

# Check if the container exists
if ! docker ps | grep -q "$CONTAINER_ID"; then
  echo "Error: Container $CONTAINER_ID not found"
  echo "Please provide the correct container ID using --container-id"
  exit 1
fi

# Create a requirements file for the agent approach
echo "Creating requirements file for the agent approach..."
cat > agent_requirements.txt << EOF
langchain==0.1.0
langchain_mcp_adapters==0.0.10
langchain-openai>=0.0.2
aiohttp>=3.8.5
EOF

# Copy the script and requirements to the container
echo "Copying files to the container..."
docker cp agent_angus_communication.py "$CONTAINER_ID:/app/"
docker cp agent_requirements.txt "$CONTAINER_ID:/app/"

# Install the required packages
echo "Installing required packages..."
docker exec -it "$CONTAINER_ID" pip install -r /app/agent_requirements.txt

# Run the script
echo "Running the agent communication script..."
docker exec -it "$CONTAINER_ID" python /app/agent_angus_communication.py --agent-id "$AGENT_ID" --wait-for-agents "$WAIT_FOR_AGENTS" --server-url "$SERVER_URL"

echo
echo "Communication completed"
