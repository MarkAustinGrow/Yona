@echo off
REM Script to run the agent_angus_communication.py script in the Docker container

REM Set default values
set CONTAINER_ID=59ff25c1a6a5
set AGENT_ID=yona
set WAIT_FOR_AGENTS=2
set SERVER_URL=http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse

REM Parse command line arguments
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
if "%~1"=="--wait-for-agents" (
    set WAIT_FOR_AGENTS=%~2
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
if "%~1"=="--help" (
    echo Usage: %0 [options]
    echo Options:
    echo   --container-id ID      Docker container ID (default: 59ff25c1a6a5^)
    echo   --agent-id ID          Agent ID to use (default: yona^)
    echo   --wait-for-agents N    Number of agents to wait for (default: 2^)
    echo   --server-url URL       Coral server URL (default: http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse^)
    echo   --help                 Show this help message
    exit /b 0
)
echo Unknown option: %~1
echo Use --help for usage information
exit /b 1
:end_parse_args

echo === Running Agent-Based Communication with Angus via Coral Protocol ===
echo Container ID: %CONTAINER_ID%
echo Agent ID: %AGENT_ID%
echo Wait for agents: %WAIT_FOR_AGENTS%
echo Server URL: %SERVER_URL%
echo.

REM Check if the container exists
docker ps | findstr %CONTAINER_ID% > nul
if errorlevel 1 (
    echo Error: Container %CONTAINER_ID% not found
    echo Please provide the correct container ID using --container-id
    exit /b 1
)

REM Create a requirements file for the agent approach
echo Creating requirements file for the agent approach...
(
    echo langchain==0.1.0
    echo langchain_mcp_adapters==0.0.10
    echo langchain-openai^>=0.0.2
    echo aiohttp^>=3.8.5
) > agent_requirements.txt

REM Copy the script and requirements to the container
echo Copying files to the container...
docker cp agent_angus_communication.py %CONTAINER_ID%:/app/
docker cp agent_requirements.txt %CONTAINER_ID%:/app/

REM Install the required packages
echo Installing required packages...
docker exec -it %CONTAINER_ID% pip install -r /app/agent_requirements.txt

REM Run the script
echo Running the agent communication script...
docker exec -it %CONTAINER_ID% python /app/agent_angus_communication.py --agent-id "%AGENT_ID%" --wait-for-agents %WAIT_FOR_AGENTS% --server-url "%SERVER_URL%"

echo.
echo Communication completed
