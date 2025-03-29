# Accessing Logs on the Linode Server

This guide explains how to access and view logs for the Yona application deployed on the Linode server.

## 1. Accessing Docker Container Logs

Docker container logs capture the stdout and stderr output from the containers. These logs include application startup messages, errors, and any output written to the console.

### 1.1 View Logs for All Services

```bash
# SSH into your Linode server
ssh yona@your-linode-ip

# Navigate to the application directory
cd ~/yona

# View logs for all services
docker-compose logs

# Follow logs in real-time (press Ctrl+C to exit)
docker-compose logs -f
```

### 1.2 View Logs for Specific Services

```bash
# View logs for the API service
docker-compose logs yona-api

# View logs for the feedback processor service
docker-compose logs yona-feedback-processor

# Follow logs for a specific service in real-time
docker-compose logs -f yona-api
```

### 1.3 View Logs with Timestamps

```bash
# View logs with timestamps
docker-compose logs --timestamps

# View the last 100 lines of logs
docker-compose logs --tail=100
```

## 2. Accessing Application Log Files

The application writes log files to the `./logs` directory, which is mounted as a volume in both containers. These log files can be accessed directly on the server.

```bash
# SSH into your Linode server
ssh yona@your-linode-ip

# Navigate to the logs directory
cd ~/yona/logs

# List all log files
ls -la

# View the content of a specific log file
cat feedback_processor.log

# View the last 50 lines of a log file
tail -n 50 feedback_processor.log

# Follow a log file in real-time (press Ctrl+C to exit)
tail -f feedback_processor.log
```

## 3. Accessing Supabase Logs

The application also logs to the Supabase `yona_logs` table. These logs can be viewed through the Supabase dashboard or by querying the table directly.

### 3.1 View Logs in Supabase Dashboard

1. Log in to the [Supabase Dashboard](https://app.supabase.io)
2. Select your project
3. Go to the "Table Editor" in the left sidebar
4. Select the "yona_logs" table
5. Use the filters and sorting options to find specific logs

### 3.2 Query Logs Using SQL

You can also use SQL to query the logs table directly from the Supabase SQL Editor:

```sql
-- View the most recent logs
SELECT * FROM yona_logs
ORDER BY timestamp DESC
LIMIT 100;

-- View logs for a specific level (e.g., ERROR)
SELECT * FROM yona_logs
WHERE level = 'ERROR'
ORDER BY timestamp DESC;

-- View logs from a specific source
SELECT * FROM yona_logs
WHERE source = 'src.agent'
ORDER BY timestamp DESC
LIMIT 50;

-- View logs from a specific time period
SELECT * FROM yona_logs
WHERE timestamp BETWEEN '2025-03-28T00:00:00' AND '2025-03-29T23:59:59'
ORDER BY timestamp DESC;
```

## 4. Log Rotation and Management

The server is configured with logrotate to manage log files and prevent them from consuming too much disk space. Log files are rotated daily and kept for 14 days.

To check the status of log rotation:

```bash
# SSH into your Linode server
ssh yona@your-linode-ip

# Check logrotate status
sudo logrotate -d /etc/logrotate.d/yona
```

## 5. Monitoring Disk Space Used by Logs

To check how much disk space is being used by logs:

```bash
# SSH into your Linode server
ssh yona@your-linode-ip

# Check disk usage of the logs directory
du -sh ~/yona/logs

# Check overall disk usage
df -h
```

## 6. Troubleshooting Common Log Issues

### 6.1 Missing Logs

If logs are not being generated:

1. Check if the application is running:
   ```bash
   docker-compose ps
   ```

2. Verify that the log directory exists and has proper permissions:
   ```bash
   ls -la ~/yona/logs
   ```

3. Restart the services:
   ```bash
   docker-compose restart
   ```

### 6.2 Log File Too Large

If a log file becomes too large:

1. Rotate the log manually:
   ```bash
   sudo logrotate -f /etc/logrotate.d/yona
   ```

2. Consider increasing the frequency of log rotation or decreasing the retention period in the logrotate configuration.
