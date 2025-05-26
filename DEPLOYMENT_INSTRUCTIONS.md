# Deployment Instructions for Linode Server

These instructions will guide you through the process of deploying the latest changes to the Linode server.

## Prerequisites

- SSH access to the Linode server
- Git access to the repository
- Docker and Docker Compose installed on the server

## Deployment Steps

1. **Pull the latest changes from GitHub**

   ```bash
   # Navigate to the repository directory (if not already there)
   cd /opt/yona

   # Pull the latest changes
   git pull origin coral_integration2
   ```

2. **Make the deployment script executable**

   ```bash
   chmod +x deploy_from_github.sh
   ```

3. **Run the deployment script**

   ```bash
   # To see all available options
   ./deploy_from_github.sh --help

   # To perform all actions (pull, build, restart)
   ./deploy_from_github.sh --all

   # To only restart the containers without rebuilding
   ./deploy_from_github.sh --restart
   ```

4. **Verify the deployment**

   ```bash
   # Check the status of the containers
   docker ps

   # View the logs
   ./deploy_from_github.sh --logs
   ```

## Testing the Angus Communication

After deploying, you can run the Angus communication tests:

1. **Make the test scripts executable**

   ```bash
   chmod +x test_angus_*.py
   ```

2. **Copy a test script to the Docker container**

   ```bash
   docker cp test_angus_enhanced.py yona_yona-coral_1:/app/
   ```

3. **Run the test inside the container**

   ```bash
   docker exec -it yona_yona-coral_1 python test_angus_enhanced.py
   ```

4. **View the logs**

   ```bash
   docker exec -it yona_yona-coral_1 cat angus_enhanced_test.log
   ```

5. **Try multiple agent IDs**

   ```bash
   docker cp test_angus_multiple_ids.py yona_yona-coral_1:/app/
   docker exec -it yona_yona-coral_1 python test_angus_multiple_ids.py
   ```

## Troubleshooting

If you encounter any issues:

1. **Check the logs**

   ```bash
   docker logs yona_yona-coral_1
   ```

2. **Verify the container is running**

   ```bash
   docker ps
   ```

3. **Check for any error messages in the test logs**

   ```bash
   docker exec -it yona_yona-coral_1 cat angus_*_test.log
   ```

4. **Restart the container if needed**

   ```bash
   docker-compose restart yona-coral
   ```
