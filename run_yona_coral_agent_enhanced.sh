#!/bin/bash
# Script to run the enhanced Yona Coral Agent in a Docker container

# Default values
CONTAINER_ID=""
AGENT_ID="yona_agent"
SERVER_URL="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --container-id)
            CONTAINER_ID="$2"
            shift
            shift
            ;;
        --agent-id)
            AGENT_ID="$2"
            shift
            shift
            ;;
        --server-url)
            SERVER_URL="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if container ID is provided
if [ -z "$CONTAINER_ID" ]; then
    echo "Error: Container ID is required"
    echo "Usage: $0 --container-id CONTAINER_ID [--agent-id AGENT_ID] [--server-url SERVER_URL]"
    exit 1
fi

# Copy the enhanced agent script to the container
echo "Copying enhanced agent script to container..."
docker cp yona_coral_agent_enhanced.py $CONTAINER_ID:/app/yona_coral_agent_enhanced.py

# Run the enhanced agent in the container
echo "Running enhanced Yona Coral Agent in container $CONTAINER_ID..."
docker exec -it $CONTAINER_ID python /app/yona_coral_agent_enhanced.py --agent-id "$AGENT_ID" --server-url "$SERVER_URL"
