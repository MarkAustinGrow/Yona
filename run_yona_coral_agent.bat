@echo off
REM Script to run the Yona Coral Agent in a Docker container

REM Default values
set CONTAINER_ID=59ff25c1a6a5
set AGENT_ID=yona_agent
set SERVER_URL=http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse

REM Parse command-line arguments
:parse_args
if "%~1"=="" goto :end_parse_args
if "%~1"=="--container-id" (
    set CONTAINER_ID=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--agent-id" (
    set AGENT_ID=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--server-url" (
    set SERVER_URL=%~2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %~1
echo Usage: %0 [--container-id ID] [--agent-id ID] [--server-url URL]
exit /b 1
:end_parse_args

echo === Running Yona Coral Agent for Communication with Angus via Coral Protocol ===
echo Container ID: %CONTAINER_ID%
echo Agent ID: %AGENT_ID%
echo Server URL: %SERVER_URL%
echo.

REM Create requirements file for the agent approach
echo Creating requirements file for the agent approach...
(
echo langchain-core^>=0.3.36,^<0.4.0
echo langchain_mcp_adapters==0.0.10
echo langchain-openai^>=0.0.2
echo aiohttp^>=3.8.5
echo python-dotenv^>=0.21.0
) > yona_coral_requirements.txt

REM Copy files to the container
echo Copying files to the container...
docker cp yona_coral_agent.py %CONTAINER_ID%:/app/
docker cp yona_coral_requirements.txt %CONTAINER_ID%:/app/

REM Copy .env file to the container
echo Copying .env file to the container...
docker cp .env %CONTAINER_ID%:/app/

REM Install required packages
echo Installing required packages...
docker exec %CONTAINER_ID% pip install -r /app/yona_coral_requirements.txt

REM Run the agent
echo Running the Yona Coral Agent...
docker exec -it %CONTAINER_ID% python /app/yona_coral_agent.py --agent-id "%AGENT_ID%" --server-url "%SERVER_URL%"

echo Communication completed
