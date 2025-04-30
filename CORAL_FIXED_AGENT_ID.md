# Coral Protocol Integration with Fixed Agent ID

This document explains the changes made to the Coral Protocol integration to use a fixed agent ID instead of a timestamp-based ID.

## Problem

Previously, the Yona agent used a timestamp-based ID (e.g., `yona-agent-1745936151`) that changed every time the container was restarted. This made it difficult for other agents to consistently reference the Yona agent, as they would need to know the current ID.

## Solution

We've updated the Coral Protocol integration to use a fixed agent ID (`yona-agent`) that remains consistent across container restarts. This aligns with the Coral Protocol design, which uses fixed, predetermined agent IDs.

## Changes Made

1. **Updated `run_yona_coral.py`**:
   - Changed the default session ID from timestamp-based to a fixed ID
   - Added support for the `YONA_SESSION_ID` environment variable

2. **Updated `docker-compose.yml`**:
   - Added the `YONA_SESSION_ID` environment variable to the `yona-coral` service

3. **Updated `coral_client.py`**:
   - Modified the SSE connection to use the base agent ID (e.g., "yona-agent") instead of hardcoding "yona-agent"
   - Updated the event listener to use the same agent ID extraction logic

4. **Updated test scripts**:
   - Modified `simple_coral_test.py`, `test_with_new_agent_id.py`, and `auto_test_coral.py` to use the fixed agent ID

## Deployment Instructions

Follow these steps to deploy the changes to the Linode server:

1. **Pull the latest changes from GitHub**:
   ```bash
   cd /opt/yona
   git pull origin Coral_Protocol
   ```

2. **Update the Docker Compose configuration**:
   The updated `docker-compose.yml` file includes the `YONA_SESSION_ID` environment variable.

3. **Restart the Yona container**:
   ```bash
   docker-compose up -d --force-recreate yona-coral
   ```

4. **Verify the changes**:
   ```bash
   # Check the logs to confirm the agent is using the fixed ID
   docker logs yona_yona-coral_1 | grep "Creating Coral adapter with session ID"
   
   # Run the simple test script
   python3 simple_coral_test.py
   ```

## Testing

The updated test scripts now use the fixed agent ID (`yona-agent`) instead of trying to detect the current ID from logs:

- `simple_coral_test.py`: Basic test that creates a thread and sends a message
- `test_with_new_agent_id.py`: Test with multiple mention formats
- `auto_test_coral.py`: Comprehensive test that monitors for responses

Run any of these scripts to test the Coral Protocol integration:

```bash
python3 simple_coral_test.py
```

## Troubleshooting

If you encounter issues:

1. **Check the agent ID in the logs**:
   ```bash
   docker logs yona_yona-coral_1 | grep "Creating Coral adapter with session ID"
   ```
   It should show `Creating Coral adapter with session ID: yona-agent`

2. **Verify the environment variable is set**:
   ```bash
   docker inspect yona_yona-coral_1 | grep YONA_SESSION_ID
   ```

3. **Check for errors in the logs**:
   ```bash
   docker logs yona_yona-coral_1 | grep ERROR
   ```

4. **Restart the container if needed**:
   ```bash
   docker restart yona_yona-coral_1
   ```

## Benefits of This Approach

- **Consistency**: The agent ID remains the same across container restarts
- **Simplicity**: Other agents can always reference the Yona agent using the same ID
- **Alignment**: This approach aligns with the Coral Protocol design, which uses fixed agent IDs
- **Reliability**: Reduces errors caused by incorrect agent IDs
