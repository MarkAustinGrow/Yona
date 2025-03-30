# Fixing Recursive Logging Issue

This document explains the changes made to fix the recursive logging issue in the Yona application.

## Problem

After implementing the container identifiers in the logging system, we encountered a recursive logging issue:

1. The Supabase log handler was added to the root logger in the feedback processor
2. This caused all logs (including those from libraries) to be sent to Supabase
3. The `httpx` library (used to make HTTP requests to Supabase) was logging each request
4. These logs were also being sent to Supabase, creating a feedback loop
5. This resulted in a cascade of log entries for each original log message

## Solution

We modified the `SupabaseLogHandler` class in `src/logging_utils.py` to filter out logs from the `httpx` library:

```python
def emit(self, record):
    try:
        # Skip httpx logs to prevent recursive logging
        if record.name == 'httpx':
            return
        
        # Rest of the method remains unchanged...
```

This simple change prevents the recursive logging by skipping logs from the `httpx` library, while still allowing all other logs to be sent to Supabase.

## Deployment

To deploy this fix:

1. Commit the changes to GitHub:
   ```bash
   git add src/logging_utils.py LOGGING_FIX.md
   git commit -m "Fix recursive logging issue by filtering out httpx logs"
   git push origin NuroAPI
   ```

2. Pull the changes on the Linode server:
   ```bash
   ssh root@172-236-28-244
   cd /opt/yona
   git pull origin NuroAPI
   ```

3. Rebuild and restart the Docker containers:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

4. Verify the fix by checking the logs:
   ```bash
   docker-compose logs --tail=50
   ```

## Expected Results

After deploying this fix:

1. The recursive logging should stop
2. The dashboard should show a more reasonable number of log entries
3. Important application logs will still be captured and displayed
4. The container identifiers will still work correctly

This fix maintains the benefits of the container identifiers while eliminating the recursive logging issue.
