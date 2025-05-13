#!/bin/bash
# Script to run the enhanced Yona Coral Agent test in a Docker container

# Default values
CONTAINER_ID=""
AGENT_ID="angus_agent"
TARGET_AGENT_ID="yona_agent"
SERVER_URL="http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"
PROMPT="Create a happy K-pop song about summer adventures"
TEST_FRAGMENTED=false

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
        --target-agent-id)
            TARGET_AGENT_ID="$2"
            shift
            shift
            ;;
        --server-url)
            SERVER_URL="$2"
            shift
            shift
            ;;
        --prompt)
            PROMPT="$2"
            shift
            shift
            ;;
        --test-fragmented)
            TEST_FRAGMENTED=true
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
    echo "Usage: $0 --container-id CONTAINER_ID [--agent-id AGENT_ID] [--target-agent-id TARGET_AGENT_ID] [--server-url SERVER_URL] [--prompt PROMPT] [--test-fragmented]"
    exit 1
fi

# Copy the enhanced test script to the container
echo "Copying enhanced test script to container..."
docker cp test_yona_coral_agent_enhanced.py $CONTAINER_ID:/app/test_yona_coral_agent_enhanced.py

# Build the command
CMD="python /app/test_yona_coral_agent_enhanced.py --agent-id \"$AGENT_ID\" --target-agent-id \"$TARGET_AGENT_ID\" --server-url \"$SERVER_URL\" --prompt \"$PROMPT\""

# Add the test-fragmented flag if enabled
if [ "$TEST_FRAGMENTED" = true ]; then
    CMD="$CMD --test-fragmented"
fi

# Run the enhanced test in the container
echo "Running enhanced Yona Coral Agent test in container $CONTAINER_ID..."
docker exec -it $CONTAINER_ID bash -c "$CMD"
