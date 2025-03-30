# Docker Container Time Zone Fix

This document explains the changes made to fix the time zone issue in the Yona Docker containers.

## Problem

The Docker containers were running in UTC time zone, while the dashboard was displaying logs in the local time zone (Europe/London, UTC+1 during daylight saving time). This caused confusion in the logs, particularly with messages like "Next processing cycle will run at..." where the time mentioned in the message didn't match the timestamp of the log entry.

For example, a log entry timestamped at 13:16:58 (local time) would say "Next processing cycle will run at 2025-03-30 12:16:58", making it appear as if the next cycle would run immediately rather than an hour later.

## Solution

We modified the `docker-compose.yml` file to set the time zone for both containers to Europe/London:

```yaml
services:
  yona-api:
    # ... existing configuration ...
    environment:
      - TZ=Europe/London
    # ... rest of configuration ...

  yona-feedback-processor:
    # ... existing configuration ...
    environment:
      - TZ=Europe/London
    # ... rest of configuration ...
```

This change ensures that:

1. The containers use the same time zone as the dashboard
2. All timestamps in logs will be consistent
3. Messages like "Next processing cycle will run at..." will show times that match the log entry timestamps

## Deployment

To deploy this fix:

1. Commit the changes to GitHub:
   ```bash
   git add docker-compose.yml TIMEZONE_FIX.md
   git commit -m "Fix time zone issue in Docker containers"
   git push origin NuroAPI
   ```

2. Pull the changes on the Linode server:
   ```bash
   ssh root@172-236-28-244
   cd /opt/yona
   git pull origin NuroAPI
   ```

3. Restart the Docker containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. Verify the fix:
   ```bash
   # Check the container time
   docker-compose exec yona-feedback-processor date
   
   # Should show a time in Europe/London time zone (UTC+1 during DST)
   ```

## Expected Results

After deploying this fix:

1. The container time will match the local time (Europe/London)
2. Log messages will show times in the local time zone
3. "Next processing cycle will run at..." messages will correctly show a time that's 1 hour ahead of the current time
4. The dashboard will display consistent timestamps

This fix maintains all the functionality of the application while making the logs more intuitive and easier to understand.
