@echo off
REM Script to test the Docker setup locally

REM Ensure the logs directory exists
if not exist logs mkdir logs

echo Building Docker images...
docker-compose build

echo Starting containers...
docker-compose up -d

echo Containers started. Use the following commands to interact with them:
echo   - View logs: docker-compose logs -f
echo   - Stop containers: docker-compose down
echo   - Check container status: docker-compose ps

echo Testing API endpoints...
echo.
echo Health check endpoint:
curl -s http://localhost:5000/health

echo.
echo Capabilities endpoint:
curl -s http://localhost:5000/capabilities

echo.
echo DID document endpoint:
curl -s http://localhost:5000/.well-known/did.json

echo.
echo Containers are running. Press Ctrl+C to stop viewing logs.
docker-compose logs -f
