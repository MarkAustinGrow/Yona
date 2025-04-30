#!/usr/bin/env python3
"""
Fix Coral Session ID Script

This script diagnoses and fixes issues with the Coral Protocol session ID.
It modifies the docker-compose.yml file to explicitly set the session ID
and restarts the container to apply the changes.
"""

import os
import sys
import subprocess
import logging
import argparse
import re
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fix_coral_session_id")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fix Coral Protocol session ID")
    parser.add_argument("--session-id", default="yona-agent", help="Fixed session ID to use")
    parser.add_argument("--container-name", default="yona_yona-coral_1", help="Docker container name")
    parser.add_argument("--docker-compose-file", default="docker-compose.yml", help="Path to docker-compose.yml")
    parser.add_argument("--backup", action="store_true", help="Create backup of docker-compose.yml")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def run_command(command, check=True):
    """Run a shell command and return the result."""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=True
        )
        if result.stdout:
            logger.info(f"Command output: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Command error output: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {e}")
        logger.error(f"Error output: {e.stderr}")
        raise

def check_current_state(container_name):
    """Check the current state of the system."""
    logger.info("Checking current state of the system")
    
    # Check if the container is running
    result = run_command(f"docker ps | grep {container_name}", check=False)
    if result.returncode != 0:
        logger.warning(f"Container {container_name} is not running")
    else:
        logger.info(f"Container {container_name} is running")
    
    # Check the logs for the session ID
    result = run_command(f"docker logs {container_name} | grep 'Creating Coral adapter with session ID'", check=False)
    if result.returncode == 0:
        session_id_match = re.search(r'Creating Coral adapter with session ID: ([\w-]+)', result.stdout)
        if session_id_match:
            current_session_id = session_id_match.group(1)
            logger.info(f"Current session ID: {current_session_id}")
        else:
            logger.warning("Could not extract session ID from logs")
    else:
        logger.warning("Could not find session ID in logs")
    
    # Check environment variables in the container
    result = run_command(f"docker inspect {container_name} | grep -A 10 'Env'", check=False)
    if result.returncode == 0:
        env_match = re.search(r'YONA_SESSION_ID=([^"]+)', result.stdout)
        if env_match:
            env_session_id = env_match.group(1)
            logger.info(f"YONA_SESSION_ID environment variable: {env_session_id}")
        else:
            logger.warning("YONA_SESSION_ID environment variable not found")
    else:
        logger.warning("Could not inspect container environment variables")
    
    # Check the command used to start the container
    result = run_command(f"docker inspect {container_name} | grep -A 3 'Cmd'", check=False)
    if result.returncode == 0:
        logger.info(f"Container command: {result.stdout.strip()}")
    else:
        logger.warning("Could not inspect container command")

def modify_docker_compose(docker_compose_file, session_id, create_backup=False):
    """Modify the docker-compose.yml file to explicitly set the session ID."""
    logger.info(f"Modifying {docker_compose_file} to use session ID: {session_id}")
    
    # Create backup if requested
    if create_backup:
        backup_file = f"{docker_compose_file}.bak"
        logger.info(f"Creating backup at {backup_file}")
        run_command(f"cp {docker_compose_file} {backup_file}")
    
    # Read the current file
    with open(docker_compose_file, 'r') as f:
        content = f.read()
    
    # Check if the command already includes --session
    if re.search(r'command:.*--session', content):
        logger.info("Command already includes --session parameter, updating it")
        # Replace the existing --session parameter
        new_content = re.sub(
            r'(command:.*run_yona_coral\.py.*--session) +[\w-]+',
            r'\1 ' + session_id,
            content
        )
    else:
        logger.info("Adding --session parameter to command")
        # Add the --session parameter to the command
        new_content = re.sub(
            r'(command:.*run_yona_coral\.py.*)(--continuous)',
            r'\1--session ' + session_id + r' \2',
            content
        )
    
    # Write the modified content back to the file
    with open(docker_compose_file, 'w') as f:
        f.write(new_content)
    
    logger.info(f"Successfully updated {docker_compose_file}")

def restart_container(container_name):
    """Restart the container to apply the changes."""
    logger.info(f"Restarting container {container_name}")
    
    # Stop the container
    run_command(f"docker stop {container_name}", check=False)
    
    # Remove the container
    run_command(f"docker rm {container_name}", check=False)
    
    # Start the container with docker-compose
    run_command("docker-compose up -d")
    
    # Wait for the container to start
    logger.info("Waiting for container to start...")
    time.sleep(5)
    
    # Check if the container is running
    result = run_command(f"docker ps | grep {container_name}", check=False)
    if result.returncode == 0:
        logger.info(f"Container {container_name} is running")
    else:
        logger.error(f"Container {container_name} failed to start")
        return False
    
    return True

def verify_changes(container_name, session_id):
    """Verify that the changes were applied correctly."""
    logger.info("Verifying changes")
    
    # Wait for the container to initialize
    logger.info("Waiting for container to initialize...")
    time.sleep(5)
    
    # Check the logs for the session ID
    result = run_command(f"docker logs {container_name} | grep 'Creating Coral adapter with session ID'", check=False)
    if result.returncode == 0:
        session_id_match = re.search(r'Creating Coral adapter with session ID: ([\w-]+)', result.stdout)
        if session_id_match:
            current_session_id = session_id_match.group(1)
            logger.info(f"New session ID: {current_session_id}")
            if current_session_id == session_id:
                logger.info("Session ID was successfully updated!")
                return True
            else:
                logger.warning(f"Session ID is still not correct. Expected: {session_id}, Got: {current_session_id}")
        else:
            logger.warning("Could not extract session ID from logs")
    else:
        logger.warning("Could not find session ID in logs")
    
    return False

def main():
    """Main function."""
    args = parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Check current state
        check_current_state(args.container_name)
        
        # Modify docker-compose.yml
        modify_docker_compose(args.docker_compose_file, args.session_id, args.backup)
        
        # Restart container
        if restart_container(args.container_name):
            # Verify changes
            if verify_changes(args.container_name, args.session_id):
                logger.info("Fix completed successfully!")
                return 0
            else:
                logger.error("Fix failed: Session ID was not updated correctly")
                return 1
        else:
            logger.error("Fix failed: Could not restart container")
            return 1
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
