# Coral Protocol Docker Integration Guide

## Overview

This guide explains how to use the updated Docker configuration that includes full Coral Protocol support for Yona.

## What's New

### Updated Dependencies
- Added `langchain_mcp_adapters==0.0.11` to requirements.txt
- Added `aiohttp>=3.8.5` for async HTTP support
- All coral protocol dependencies are now automatically installed in Docker containers

### New Docker Services
- **yona-coral-agent**: A dedicated service for running Yona as a Coral Protocol agent
- Uses the correct server URL: `http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse`

## Quick Start

### 1. Deploy Updated Containers

```bash
# Make the deployment script executable
chmod +x deploy_coral_docker.sh

# Run the deployment
./deploy_coral_docker.sh
```

This will:
- Stop existing containers
- Rebuild with coral protocol dependencies
- Start the main services (API and feedback processor)
- Show status and helpful commands

### 2. Test Coral Protocol Connection

```bash
# Enter the API container
docker exec -it $(docker-compose ps -q yona-api) bash

# Test the connection
python test_coral_langchain.py --server-url http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse --test connection
```

### 3. Start Coral Agent Service (Optional)

```bash
# Start the dedicated coral agent service
docker-compose --profile coral up -d yona-coral-agent

# View coral agent logs
docker-compose --profile coral logs -f yona-coral-agent
```

## Available Services

### Main Services (Always Running)
- **yona-api**: Main API server on port 5000
- **yona-feedback-processor**: Background feedback processing

### Coral Services (Optional)
- **yona-coral-agent**: Dedicated coral protocol agent (use `--profile coral`)

## Testing Coral Protocol

### Basic Connection Test
```bash
docker exec -it $(docker-compose ps -q yona-api) bash
python test_coral_langchain.py --server-url http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse --test connection
```

### Enhanced Agent Test
```bash
docker exec -it $(docker-compose ps -q yona-api) bash
python yona_coral_agent_enhanced.py --server-url http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse --agent-id yona
```

### Agent Capabilities Test
```bash
docker exec -it $(docker-compose ps -q yona-api) bash
python test_coral_langchain.py --server-url http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse --test capabilities --agent-did did:web:yona.ai
```

### Function Call Test
```bash
docker exec -it $(docker-compose ps -q yona-api) bash
python test_coral_langchain.py --server-url http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse --test call --agent-did did:web:yona.ai --function create_song --args '{"prompt": "test song"}'
```

## Coral Server Configuration

### Correct Server URL
```
http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse
```

### URL Components
- **Host**: `coral.pushcollective.club`
- **Port**: `5555`
- **Application ID**: `app`
- **Privacy Key**: `priv`
- **Session**: `session1`
- **Endpoint**: `sse` (Server-Sent Events)

## Troubleshooting

### Missing Dependencies Error
If you see `Error: langchain_mcp_adapters package not installed`, rebuild the containers:
```bash
./deploy_coral_docker.sh
```

### Connection Issues
1. Verify the coral server is accessible:
   ```bash
   curl -H "Accept: text/event-stream" "http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse"
   ```

2. Check container logs:
   ```bash
   docker-compose logs yona-api
   docker-compose --profile coral logs yona-coral-agent
   ```

### File Not Found Errors
Some coral test files are only available on the host system. Use the main test script:
```bash
python test_coral_langchain.py
```

## Manual Commands

### Rebuild Containers
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Start Specific Services
```bash
# Main services only
docker-compose up -d yona-api yona-feedback-processor

# Include coral agent
docker-compose --profile coral up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f yona-api
docker-compose --profile coral logs -f yona-coral-agent
```

### Enter Container
```bash
# API container
docker exec -it $(docker-compose ps -q yona-api) bash

# Coral agent container (if running)
docker exec -it $(docker-compose ps -q yona-coral-agent) bash
```

## Development Workflow

### 1. Code Changes
Make changes to your coral protocol code locally.

### 2. Rebuild and Deploy
```bash
./deploy_coral_docker.sh
```

### 3. Test
```bash
docker exec -it $(docker-compose ps -q yona-api) bash
python test_coral_langchain.py --server-url http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse --test connection
```

### 4. Monitor
```bash
docker-compose logs -f yona-api
```

## Production Deployment

### On Your Linode Server
```bash
# Navigate to your project
cd /opt/yona

# Pull latest changes
git pull origin coral_protocol_langchain

# Deploy with coral support
./deploy_coral_docker.sh

# Start coral agent if needed
docker-compose --profile coral up -d yona-coral-agent
```

## Key Features

### Automatic Dependency Management
- All coral protocol dependencies are installed automatically
- No manual pip installs required in containers
- Consistent environment across all services

### Flexible Service Architecture
- Main services run by default
- Coral agent service available on-demand with profiles
- Easy to scale and manage individual components

### Comprehensive Testing
- Multiple test scripts available in containers
- Correct server URLs pre-configured
- Easy debugging and monitoring

## Next Steps

1. **Deploy the updated containers** using `./deploy_coral_docker.sh`
2. **Test the coral protocol connection** to verify everything works
3. **Start the coral agent service** if you want persistent coral protocol connectivity
4. **Monitor logs** to ensure stable operation
5. **Integrate with other agents** on the coral protocol network

Your Yona installation now has full Coral Protocol support with proper dependency management and easy deployment!
