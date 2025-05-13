# Coral Agent Update Instructions

This document provides instructions for updating the Yona Coral Agent on the Linode server to fix the issue with string mentions.

## Overview of Changes

The following changes have been made to fix the issue with the Yona Coral Agent:

1. **Fixed Tool Invocation Method**: Changed from `client.connections["coral"].invoke_tool()` to `tool.ainvoke()` to match the updated API.

2. **Added Support for String Mentions**: Modified the code to handle both string and dictionary mentions from the Coral server.

3. **Improved Thread ID Handling**: Added fallback mechanisms for when thread IDs aren't available, including creating new threads when needed.

4. **Enhanced Logging**: Added detailed logging to help debug issues with the mention format.

## Pulling Changes to the Linode Server

Follow these steps to pull the changes to the Linode server:

1. **SSH into the Linode Server**:
   ```bash
   ssh root@coral.pushcollective.club
   ```

2. **Navigate to the Yona Directory**:
   ```bash
   cd /opt/yona
   ```

3. **Pull the Latest Changes from GitHub**:
   ```bash
   # Make sure you're on the coral_protocol_langchain branch
   git checkout coral_protocol_langchain

   # Pull the latest changes
   git pull origin coral_protocol_langchain
   ```

4. **Make the Shell Scripts Executable**:
   ```bash
   # Make the shell scripts executable
   chmod +x run_yona_coral_agent.sh run_test_yona_coral_agent.sh
   ```

5. **Run the Yona Coral Agent**:
   ```bash
   # Run the agent using the Docker script with the correct container ID
   ./run_yona_coral_agent.sh --container-id 59ff25c1a6a5
   ```

## Testing the Changes

To test the changes, you can use the test script:

```bash
# Run the test script with the correct container ID
./run_test_yona_coral_agent.sh --container-id 59ff25c1a6a5
```

This will:
1. Connect to the Coral server
2. List all registered agents
3. Check if the Yona agent is connected
4. Create a thread with the Yona agent
5. Send a function call to create a song
6. Wait for a response
7. Display the song data

## Troubleshooting

If you encounter any issues:

1. **Check the Logs**: Look for detailed logs about the mention format.

2. **Verify the Container ID**: Make sure you're using the correct container ID.

3. **Check the Server URL**: Make sure the server URL is correct.

4. **Restart the Agent**: Try restarting the agent if it's not responding.

5. **Check the OpenAI API Key**: Make sure the OpenAI API key is set in the `.env` file.

## Coordination with Team Angus

For successful communication with Team Angus:

1. **Coordinate Timing**: Arrange a specific time for testing when both agents will be running.

2. **Confirm Agent IDs**: Confirm that Team Angus is using "angus_agent" as their agent ID and that they're expecting "yona_agent" as your agent ID.

3. **Confirm Server URL**: Confirm that both teams are using the same server URL and session ID.

4. **Test Independently**: Test your agent independently using the test script before coordinating with Team Angus.

5. **Monitor Logs**: Monitor the logs for any issues during the test.
