# Instructions for Reverting to NuroAPI Branch

These instructions will guide you through the process of reverting to the NuroAPI branch both locally and on the Linode server.

## Local Repository

You've already successfully switched to the NuroAPI branch locally:

```bash
git checkout NuroAPI
git pull origin NuroAPI
```

## Linode Server

### Option 1: Using the Script

You can use the provided script to revert to the NuroAPI branch on the server. Since you're on Windows, you'll need to copy the script to the server first:

1. **Copy the script to the server**:
   ```bash
   scp revert_to_nuroapi.sh root@172-236-28-244:/opt/yona/
   ```

2. **SSH into the server**:
   ```bash
   ssh root@172-236-28-244
   ```

3. **Make the script executable**:
   ```bash
   cd /opt/yona
   chmod +x revert_to_nuroapi.sh
   ```

4. **Run the script**:
   ```bash
   # To see all available options
   ./revert_to_nuroapi.sh --help

   # To perform all actions (revert, build, restart)
   ./revert_to_nuroapi.sh --all

   # To only revert and restart without rebuilding
   ./revert_to_nuroapi.sh --revert --restart
   ```

### Option 2: Manual Commands

If you prefer to run the commands manually:

1. **SSH into the server**:
   ```bash
   ssh root@172-236-28-244
   ```

2. **Navigate to the repository directory**:
   ```bash
   cd /opt/yona
   ```

3. **Revert to the NuroAPI branch**:
   ```bash
   git fetch
   git checkout NuroAPI
   git pull origin NuroAPI
   ```

4. **Rebuild and restart the Docker containers**:
   ```bash
   docker-compose build
   docker-compose down
   docker-compose up -d
   ```

5. **Verify the containers are running**:
   ```bash
   docker ps
   ```

## Verification

After reverting to the NuroAPI branch and restarting the containers, you can verify that everything is working correctly:

1. **Check the container logs**:
   ```bash
   docker-compose logs -f
   ```

2. **Test the API**:
   ```bash
   curl http://localhost:5000/health
   ```

## Troubleshooting

If you encounter any issues:

1. **Check the container status**:
   ```bash
   docker ps -a
   ```

2. **View detailed logs for a specific container**:
   ```bash
   docker logs yona_yona-api_1
   ```

3. **Restart a specific container**:
   ```bash
   docker-compose restart yona-api
   ```
