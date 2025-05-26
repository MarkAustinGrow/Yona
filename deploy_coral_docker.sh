#!/bin/bash

echo "🚀 Deploying Yona with Coral Protocol Support"
echo "=============================================="

# Stop existing containers
echo "📦 Stopping existing containers..."
docker-compose down

# Rebuild containers with new dependencies
echo "🔨 Rebuilding containers with coral protocol dependencies..."
docker-compose build --no-cache

# Start the main services
echo "🌟 Starting main services (API and feedback processor)..."
docker-compose up -d yona-api yona-feedback-processor

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Available services:"
echo "  - yona-api: Running on port 5000"
echo "  - yona-feedback-processor: Running in background"
echo "  - yona-coral-agent: Available with 'coral' profile"
echo ""
echo "🧪 To test coral protocol:"
echo "  docker exec -it \$(docker-compose ps -q yona-api) bash"
echo "  python test_coral_langchain.py --server-url http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse --test connection"
echo ""
echo "🐠 To start coral agent service:"
echo "  docker-compose --profile coral up -d yona-coral-agent"
echo ""
echo "📊 To view logs:"
echo "  docker-compose logs -f yona-api"
echo "  docker-compose logs -f yona-feedback-processor"
echo "  docker-compose --profile coral logs -f yona-coral-agent"
