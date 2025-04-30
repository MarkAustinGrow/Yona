# Fixing Coral Protocol Session ID Issues

This document provides instructions for fixing issues with the Coral Protocol session ID on the Linode server.

## Problem

We've identified an issue where the Coral Protocol integration is still using a timestamp-based agent ID (e.g., `yona-agent-1746025062`) instead of the fixed agent ID (`yona-agent`) that we configured. This happens despite:

1. Setting the `YONA_SESSION_ID` environment variable in docker-compose.yml
2. Updating run_yona_coral.py to use this environment variable
3. Updating the test scripts to use the fixed agent ID

## Solution

We've created a script called `fix_coral_session_id.py` that:

1. Diagnoses the current state of the system
2. Modifies the docker-compose.yml file to explicitly set the session ID via command-line arguments
3. Restarts the container
4. Verifies that the changes were applied correctly

This approach bypasses any potential issues with environment variables by explicitly setting the session ID in the command line arguments, which should take precedence over any other method.

## Instructions

Follow these steps to fix the session ID issue on the Linode server:

1. **Pull the latest changes from GitHub**:
   ```bash
   cd /opt/yona
   git pull origin Coral_Protocol
   ```

2. **Run the fix script with a backup**:
   ```bash
   python3 fix_coral_session_id.py --backup
   ```
   This will:
   - Check the current state of the system
   - Create a backup of docker-compose.yml
   - Modify docker-compose.yml to explicitly set the session ID
   - Restart the container
   - Verify that the changes were applied correctly

3. **Check the logs**:
   ```bash
   docker logs yona_yona-coral_1 | grep "Creating Coral adapter with session ID"
   ```
   You should see: `Creating Coral adapter with session ID: yona-agent`

4. **Test the integration**:
   ```bash
   python3 simple_coral_test.py
   ```
   This should create a thread with the Yona agent and send a test message.

## Troubleshooting

If the fix script doesn't resolve the issue:

1. **Check the script logs**:
   The script logs detailed information about what it's doing and any errors it encounters.

2. **Run with verbose logging**:
   ```bash
   python3 fix_coral_session_id.py --backup --verbose
   ```

3. **Check the local modifications to src/coral_adapter.py**:
   ```bash
   git diff src/coral_adapter.py
   ```
   There might be local changes that are affecting how the session ID is used.

4. **Manually modify the docker-compose.yml file**:
   ```bash
   # Edit the file
   nano docker-compose.yml
   
   # Change the command line to explicitly set the session ID
   # From:
   # command: python run_yona_coral.py --continuous
   # To:
   # command: python run_yona_coral.py --session yona-agent --continuous
   
   # Restart the container
   docker-compose up -d --force-recreate yona-coral
   ```

5. **Check the run_yona_coral.py file**:
   ```bash
   cat run_yona_coral.py | grep "session"
   ```
   Make sure it's correctly using the environment variable:
   ```python
   parser.add_argument('--session', default=os.environ.get('YONA_SESSION_ID', 'yona-agent'), help='Session ID')
   ```

## Additional Options

The fix script supports several command-line options:

```
usage: fix_coral_session_id.py [-h] [--session-id SESSION_ID]
                              [--container-name CONTAINER_NAME]
                              [--docker-compose-file DOCKER_COMPOSE_FILE]
                              [--backup] [--verbose]

Fix Coral Protocol session ID

optional arguments:
  -h, --help            show this help message and exit
  --session-id SESSION_ID
                        Fixed session ID to use
  --container-name CONTAINER_NAME
                        Docker container name
  --docker-compose-file DOCKER_COMPOSE_FILE
                        Path to docker-compose.yml
  --backup              Create backup of docker-compose.yml
  --verbose             Enable verbose logging
```

For example, to use a different session ID:

```bash
python3 fix_coral_session_id.py --session-id my-custom-agent --backup
```

## Why This Approach Works

By explicitly setting the session ID in the command line arguments, we ensure that it takes precedence over any other method of setting the session ID, including:

1. Environment variables
2. Default values in the code
3. Any local modifications to the code

This approach is more robust and less likely to be affected by other changes to the system.
