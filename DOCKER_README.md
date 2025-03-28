# Docker Setup for Yona

This document provides information about the Docker setup for the Yona application.

## Files

- `Dockerfile`: Defines how to build the Docker image for the Yona application
- `docker-compose.yml`: Defines the services for the Yona application
- `.dockerignore`: Specifies files and directories to exclude from the Docker build context
- `test_docker.bat`: Windows batch script to test the Docker setup locally
- `test_docker.sh`: Bash script to test the Docker setup locally (for Linux/macOS)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Services

The Docker Compose setup includes two services:

1. **yona-api**: Runs the API server that serves the capability document and DID document
   - Exposes port 5000
   - Uses the .env file for environment variables
   - Mounts the logs directory

2. **yona-feedback-processor**: Runs the continuous feedback processor
   - Uses the .env file for environment variables
   - Mounts the logs directory

## Environment Variables

The Docker Compose setup uses the .env file for environment variables. This file should contain:

```
# YouTube API Credentials
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# MusicAPI/Suno API Key
MUSICAPI_KEY=your_musicapi_key

# OpenAI API Key
OPENAI_KEY=your_openai_key

# Supabase Credentials
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

**Important**: The .env file is excluded from the Docker image via .dockerignore for security reasons.

## Testing Locally

### Windows

Run the test_docker.bat script:

```
test_docker.bat
```

### Linux/macOS

Make the test_docker.sh script executable and run it:

```bash
chmod +x test_docker.sh
./test_docker.sh
```

## Manual Commands

### Build the Docker Images

```bash
docker-compose build
```

### Start the Containers

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f
```

### Stop the Containers

```bash
docker-compose down
```

### Check Container Status

```bash
docker-compose ps
```

## API Endpoints

Once the containers are running, you can access the following endpoints:

- Health check: http://localhost:5000/health
- Capabilities: http://localhost:5000/capabilities
- DID document: http://localhost:5000/.well-known/did.json

## Deployment

For detailed deployment instructions, see the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) file.
