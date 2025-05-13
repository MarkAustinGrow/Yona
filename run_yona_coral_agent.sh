#!/bin/bash
# Script to run the Yona Coral Agent in a Docker container

# Default values
CONTAINER_ID="59ff25c1a6a5"
AGENT_ID="yona_agent"
SERVER_URL="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"

# Parse command-line arguments
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
    --server-url)
      SERVER_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--container-id ID] [--agent-id ID] [--server-url URL]"
      exit 1
      ;;
  esac
done

echo "=== Running Yona Coral Agent for Communication with Angus via Coral Protocol ==="
echo "Container ID: $CONTAINER_ID"
echo "Agent ID: $AGENT_ID"
echo "Server URL: $SERVER_URL"
echo

# Create requirements file for the agent approach
echo "Creating requirements file for the agent approach..."
cat > yona_coral_requirements.txt << EOF
langchain-core>=0.3.36,<0.4.0
langchain_mcp_adapters==0.0.10
langchain-openai>=0.0.2
aiohttp>=3.8.5
python-dotenv>=0.21.0
EOF

# Copy files to the container
echo "Copying files to the container..."
docker cp yona_coral_agent.py $CONTAINER_ID:/app/
docker cp yona_coral_requirements.txt $CONTAINER_ID:/app/

# Copy .env file to the container
echo "Copying .env file to the container..."
docker cp .env $CONTAINER_ID:/app/

# Install required packages
echo "Installing required packages..."
docker exec $CONTAINER_ID pip install -r /app/yona_coral_requirements.txt

# Run the agent
echo "Running the Yona Coral Agent..."
docker exec -it $CONTAINER_ID python /app/yona_coral_agent.py --agent-id "$AGENT_ID" --server-url "$SERVER_URL"

echo "Communication completed"
