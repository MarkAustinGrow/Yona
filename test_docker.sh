#!/bin/bash
# Script to test the Docker setup locally

# Ensure the logs directory exists
mkdir -p logs

echo "Building Docker images..."
docker-compose build

echo "Starting containers..."
docker-compose up -d

echo "Containers started. Use the following commands to interact with them:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop containers: docker-compose down"
echo "  - Check container status: docker-compose ps"

echo "Testing API endpoints..."
echo -e "\nHealth check endpoint:"
curl -s http://localhost:5000/health | jq . || echo "Failed to access health endpoint"

echo -e "\nCapabilities endpoint:"
curl -s http://localhost:5000/capabilities | jq . || echo "Failed to access capabilities endpoint"

echo -e "\nDID document endpoint:"
curl -s http://localhost:5000/.well-known/did.json | jq . || echo "Failed to access DID document endpoint"

echo -e "\nContainers are running. Press Ctrl+C to stop viewing logs."
docker-compose logs -f
