@echo off
REM Script to run the test script for the Yona Coral Agent in a Docker container

REM Default values
set CONTAINER_ID=59ff25c1a6a5
set AGENT_ID=angus_agent
set TARGET_AGENT_ID=yona_agent
set SERVER_URL=http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse
set PROMPT=Create a happy K-pop song about summer adventures

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
if "%~1"=="--target-agent-id" (
    set TARGET_AGENT_ID=%~2
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
if "%~1"=="--prompt" (
    set PROMPT=%~2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %~1
echo Usage: %0 [--container-id ID] [--agent-id ID] [--target-agent-id ID] [--server-url URL] [--prompt PROMPT]
exit /b 1
:end_parse_args

echo === Running Test for Yona Coral Agent ===
echo Container ID: %CONTAINER_ID%
echo Agent ID: %AGENT_ID%
echo Target Agent ID: %TARGET_AGENT_ID%
echo Server URL: %SERVER_URL%
echo Prompt: %PROMPT%
echo.

REM Create requirements file for the test script
echo Creating requirements file for the test script...
(
echo langchain-core^>=0.3.36,^<0.4.0
echo langchain_mcp_adapters==0.0.10
echo langchain-openai^>=0.0.2
echo aiohttp^>=3.8.5
echo python-dotenv^>=0.21.0
) > test_yona_coral_requirements.txt

REM Copy files to the container
echo Copying files to the container...
docker cp test_yona_coral_agent.py %CONTAINER_ID%:/app/
docker cp test_yona_coral_requirements.txt %CONTAINER_ID%:/app/

REM Copy .env file to the container
echo Copying .env file to the container...
docker cp .env %CONTAINER_ID%:/app/

REM Install required packages
echo Installing required packages...
docker exec %CONTAINER_ID% pip install -r /app/test_yona_coral_requirements.txt

REM Run the test script
echo Running the test script...
docker exec -it %CONTAINER_ID% python /app/test_yona_coral_agent.py --agent-id "%AGENT_ID%" --target-agent-id "%TARGET_AGENT_ID%" --server-url "%SERVER_URL%" --prompt "%PROMPT%"

echo Test completed
