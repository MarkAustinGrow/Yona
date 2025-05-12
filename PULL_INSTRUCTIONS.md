# Instructions for Pulling Changes from GitHub

These instructions will help you pull the latest changes from GitHub to the server.

## Basic Pull Command

```bash
git pull origin coral_protocol_langchain
```

This command will fetch and merge the latest changes from the `coral_protocol_langchain` branch on GitHub.

## Step-by-Step Instructions

1. **Navigate to the Yona directory**:
   ```bash
   cd /opt/yona
   ```

2. **Check your current branch**:
   ```bash
   git status
   ```
   Make sure you're on the `coral_protocol_langchain` branch.

3. **Stash any local changes** (if needed):
   ```bash
   git stash
   ```
   This will save your local changes temporarily.

4. **Pull the latest changes**:
   ```bash
   git pull origin coral_protocol_langchain
   ```

5. **Apply your stashed changes** (if needed):
   ```bash
   git stash pop
   ```
   This will reapply your local changes.

## Handling Merge Conflicts

If you encounter merge conflicts, you have a few options:

1. **Resolve the conflicts manually**:
   Edit the conflicted files to resolve the conflicts, then:
   ```bash
   git add <conflicted-files>
   git commit -m "Resolved merge conflicts"
   ```

2. **Use your changes**:
   ```bash
   git checkout --ours <conflicted-files>
   git add <conflicted-files>
   git commit -m "Used our changes for conflicts"
   ```

3. **Use the GitHub changes**:
   ```bash
   git checkout --theirs <conflicted-files>
   git add <conflicted-files>
   git commit -m "Used GitHub changes for conflicts"
   ```

## Verifying the Pull

After pulling, you should see the new files:
- test_coral_mcp.py
- CORAL_MCP_TEST_README.md
- coral_requirements.txt
- test_coral_angus.sh

You can verify this with:
```bash
ls -la
```

## Making the Shell Script Executable

After pulling, make the shell script executable:
```bash
chmod +x test_coral_angus.sh
```

## Running the Test Script

To test the communication with agent Angus:
```bash
./test_coral_angus.sh
```

Or run it with specific options:
```bash
./test_coral_angus.sh --container-id 59ff25c1a6a5 --agent-id yona --wait-for-agents 2
```

## Latest Updates (May 12, 2025)

We've fixed an issue with the test script:

1. **Fixed the MCP adapter tool invocation method**:
   - The script now uses `tool.ainvoke()` instead of `client.invoke_tool()`
   - This is compatible with langchain_mcp_adapters version 0.0.11

2. **Updated coral_requirements.txt**:
   - Changed `langchain_mcp_adapters>=0.1.0` to `langchain_mcp_adapters==0.0.11`
   - This ensures compatibility with the available version

3. **Updated agent discovery**:
   - The script now looks for the specific Angus agent ID (`69943c74-0cb8-5911-98db-79cca0bf8b7d`)
   - This makes agent discovery more reliable

To apply these fixes:

1. **Pull the latest changes**:
   ```bash
   git pull origin coral_protocol_langchain
   ```

2. **If you have a merge conflict in requirements.txt**:
   ```bash
   git checkout --theirs requirements.txt
   git add requirements.txt
   git commit -m "Resolve merge conflict in requirements.txt"
   ```

3. **Run the updated test script**:
   ```bash
   ./test_coral_angus.sh
   ```
