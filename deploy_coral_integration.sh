#!/bin/bash
# Script to deploy and test the Coral integration on the Linode server
# Usage: ./deploy_coral_integration.sh [youtube-agent-id]

set -e  # Exit on error

# Default YouTube agent ID
YOUTUBE_AGENT_ID=${1:-"youtube-agent"}
YONA_AGENT_ID="yona-agent"
CORAL_SERVER_URL="https://coral.pushcollective.club"
LOG_FILE="coral_deployment_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
for cmd in git docker docker-compose python3; do
    if ! command_exists "$cmd"; then
        log "ERROR: $cmd is required but not installed. Please install it and try again."
        exit 1
    fi
done

log "Starting Coral integration deployment"
log "YouTube Agent ID: $YOUTUBE_AGENT_ID"
log "Yona Agent ID: $YONA_AGENT_ID"

# Step 1: Pull the latest changes from GitHub
log "Pulling latest changes from GitHub..."
git fetch origin
git_status=$(git status)

if echo "$git_status" | grep -q "Your branch is up to date"; then
    log "Already up to date with remote branch."
else
    # Check for local changes
    if git diff-index --quiet HEAD --; then
        # No local changes, safe to pull
        log "Pulling latest changes..."
        git pull origin Coral_Protocol
    else
        log "Local changes detected. Stashing changes..."
        git stash
        log "Pulling latest changes..."
        git pull origin Coral_Protocol
        log "Applying stashed changes..."
        git stash pop || log "Warning: Could not apply stashed changes. Manual intervention may be required."
    fi
fi

# Step 2: Check if docker-compose.yml has the yona-coral service
if grep -q "yona-coral:" docker-compose.yml; then
    log "yona-coral service already exists in docker-compose.yml"
else
    log "Adding yona-coral service to docker-compose.yml..."
    # Create a backup of the original file
    cp docker-compose.yml docker-compose.yml.bak
    
    # Add the yona-coral service
    cat >> docker-compose.yml << 'EOF'
  
  yona-coral:
    build: .
    env_file:
      - .env
    command: python run_yona_coral.py --continuous
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
EOF
    
    log "Updated docker-compose.yml (backup saved as docker-compose.yml.bak)"
fi

# Step 3: Check if requirements.txt has the necessary dependencies
if grep -q "requests" requirements.txt && grep -q "sseclient-py" requirements.txt; then
    log "Required dependencies already in requirements.txt"
else
    log "Adding required dependencies to requirements.txt..."
    # Add dependencies if they don't exist
    grep -q "requests" requirements.txt || echo "requests>=2.25.0" >> requirements.txt
    grep -q "sseclient-py" requirements.txt || echo "sseclient-py>=1.8.0" >> requirements.txt
    log "Updated requirements.txt"
fi

# Step 4: Rebuild and restart the Coral container
log "Rebuilding and restarting the Coral container..."
docker-compose down yona-coral || log "Warning: Could not stop yona-coral container (it may not exist yet)"
docker-compose up -d --build yona-coral

# Step 5: Wait for the container to start
log "Waiting for the container to start..."
sleep 10

# Step 6: Check if the container is running
if docker-compose ps | grep -q "yona-coral" | grep -q "Up"; then
    log "Coral container is running"
else
    log "ERROR: Coral container is not running. Check the logs with 'docker-compose logs yona-coral'"
    exit 1
fi

# Step 7: Run a basic test
log "Running a basic test to verify the integration..."
if command_exists python3; then
    # Check if test_agent_communication.py exists
    if [ -f "test_agent_communication.py" ]; then
        log "Running test_agent_communication.py..."
        python3 test_agent_communication.py --yona-agent-id "$YONA_AGENT_ID" --youtube-agent-id "$YOUTUBE_AGENT_ID" --server-url "$CORAL_SERVER_URL" --wait-time 30
    else
        log "Warning: test_agent_communication.py not found. Skipping test."
    fi
else
    log "Warning: python3 not found. Skipping test."
fi

# Step 8: Show the logs
log "Showing the last 20 lines of the Coral container logs..."
docker-compose logs --tail=20 yona-coral

log "Deployment completed. To monitor the Coral container, run: docker-compose logs -f yona-coral"
log "To test the integration, run: python3 test_agent_communication.py --yona-agent-id \"$YONA_AGENT_ID\" --youtube-agent-id \"$YOUTUBE_AGENT_ID\""
log "To simulate a complete workflow, run: python3 simulate_agent_workflow.py --yona-agent-id \"$YONA_AGENT_ID\" --youtube-agent-id \"$YOUTUBE_AGENT_ID\" --simulate-responses"

exit 0
