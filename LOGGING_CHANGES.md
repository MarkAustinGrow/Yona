# Logging Changes for Yona

This document explains the changes made to the logging system to ensure that both the Yona API and Yona Feedback Processor logs are saved to the `yona_logs` table in Supabase.

## Changes Made

1. **Updated `src/logging_utils.py`**:
   - Added a `container` parameter to the `SupabaseLogHandler` class
   - Modified the `emit` method to include the container identifier in the log details

2. **Updated `src/continuous_feedback_processor.py`**:
   - Added the container identifier "feedback-processor" to the Supabase log handler
   - Added the Supabase log handler to the root logger to capture all logs from the feedback processor

3. **Updated `src/agent.py`**:
   - Added the container identifier "yona-api" to the Supabase log handler

4. **Updated `test_logging.py`**:
   - Added the container identifier "test-logging" to the Supabase log handler

## Benefits

These changes provide the following benefits:

1. **Both API and Feedback Processor logs are saved** to the `yona_logs` table
2. **Logs can be easily distinguished** by their container identifier
3. **All logs from the feedback processor** are captured, not just those from the main logger

## Deployment Instructions

To deploy these changes to the Linode server:

1. **SSH into the Linode server**:
   ```bash
   ssh yona@your-linode-ip  # or root@172-236-28-244 as shown in your terminal
   ```

2. **Navigate to the application directory**:
   ```bash
   cd /opt/yona
   ```

3. **Pull the latest changes** (if using Git):
   ```bash
   git pull
   ```
   
   Or, if not using Git, upload the modified files:
   ```bash
   # Using SCP (run this from your local machine)
   scp src/logging_utils.py src/continuous_feedback_processor.py src/agent.py test_logging.py yona@your-linode-ip:/opt/yona/
   ```

4. **Rebuild and restart the Docker containers**:
   ```bash
   # Stop the containers
   docker-compose down
   
   # Rebuild the containers
   docker-compose build
   
   # Start the containers
   docker-compose up -d
   ```

5. **Verify the changes**:
   ```bash
   # Check the logs to ensure both containers started correctly
   docker-compose logs
   
   # Check the Supabase yona_logs table to see if logs from both containers are being saved
   # You can do this through the Supabase dashboard or by running a query
   ```

## Monitoring and Troubleshooting

After deployment, you can monitor the logs to ensure they're being saved correctly:

1. **Check Docker logs**:
   ```bash
   docker-compose logs -f
   ```

2. **Check the Supabase logs table**:
   - Log in to the Supabase dashboard
   - Go to the Table Editor
   - Select the `yona_logs` table
   - Look for logs with different container identifiers in the `details` column

3. **Run a test**:
   ```bash
   # Run the test_logging.py script to verify logging is working
   docker-compose exec yona-api python test_logging.py
   ```

If you encounter any issues, check the Docker logs for error messages related to the Supabase log handler.
