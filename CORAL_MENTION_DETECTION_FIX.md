# Coral Protocol Mention Detection Fix

This document explains how to fix the mention detection issues in the Coral Protocol integration.

## Problem

The Yona agent is not detecting mentions in messages sent from other agents. This is because the current implementation only checks for mentions in the `mentions` list, but doesn't check for other mention formats like `@yona-agent` or `yona` in the message content.

## Solution

We've created two new scripts to address this issue:

1. **improved_fix_coral_adapter.py**: An improved version of the fix_coral_adapter.py script that:
   - Checks if the fix has already been applied
   - Adds more logging to help diagnose issues
   - Improves the mention detection logic to check for various mention formats

2. **test_mention_formats.py**: A test script that tries different mention formats to see which ones work with the Coral Protocol:
   - Explicit mention in API call only
   - @mention in content
   - <@mention> in content
   - Name mention in content
   - Combined mentions

## How to Apply the Fix

Follow these steps to apply the fix on the Linode server:

1. **Pull the latest changes from GitHub**:
   ```bash
   cd /opt/yona
   git pull origin Coral_Protocol
   ```

2. **Run the improved fix script with a backup**:
   ```bash
   python3 improved_fix_coral_adapter.py --backup
   ```
   This will:
   - Check if the fix has already been applied
   - Create a backup of the original file
   - Update the file with improved mention detection logic

3. **Restart the Yona container**:
   ```bash
   docker restart yona_yona-coral_1
   ```

4. **Test the mention detection**:
   ```bash
   python3 test_mention_formats.py
   ```
   This will:
   - Create a thread with the Yona agent
   - Send messages with different mention formats
   - Wait for responses

5. **Check the logs to see which mention formats were detected**:
   ```bash
   docker logs yona_yona-coral_1 | grep 'Found mention'
   ```

## What the Fix Does

The improved mention detection logic checks for mentions in various formats:

1. **Mentions list**: Checks if the agent ID is in the `mentions` list
2. **@mention**: Checks for `@agent_id` pattern in the message content
3. **<@mention>**: Checks for `<@agent_id>` pattern in the message content
4. **Name mention**: Checks for `yona` in the message content (case insensitive)
5. **Pending agent ID**: Special handling for when the agent ID is `pending`

## Troubleshooting

If you still encounter issues:

1. **Run the fix script with verbose logging**:
   ```bash
   python3 improved_fix_coral_adapter.py --backup --verbose
   ```

2. **Run the test script with verbose logging**:
   ```bash
   python3 test_mention_formats.py --verbose
   ```

3. **Check the logs for errors**:
   ```bash
   docker logs yona_yona-coral_1 | grep ERROR
   ```

4. **Force the fix to be applied even if it appears to be already applied**:
   ```bash
   python3 improved_fix_coral_adapter.py --backup --force
   ```

5. **Check if the fix was applied correctly**:
   ```bash
   cat src/coral_adapter.py | grep "Check for mentions in various formats"
   ```

## Additional Notes

- The fix is designed to be idempotent, meaning it can be applied multiple times without causing issues
- The test script is designed to help diagnose which mention formats work with the Coral Protocol
- The improved fix script adds more logging to help diagnose issues with mention detection

If you have any questions or encounter any issues, please refer to the CORAL_INTEGRATION.md document for more information.
