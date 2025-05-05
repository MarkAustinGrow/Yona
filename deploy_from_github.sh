#!/bin/bash
# Script to deploy Yona from GitHub and rebuild Docker containers

# Set variables
REPO_DIR="/opt/yona"
BRANCH="coral_integration2"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Display header
echo "====================================================="
echo "Yona Deployment Script"
echo "====================================================="
echo

# Function to display usage
function show_usage {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -p, --pull                 Pull latest changes from GitHub"
    echo "  -b, --build                Rebuild Docker containers"
    echo "  -r, --restart              Restart Docker containers"
    echo "  -a, --all                  Perform all actions (pull, build, restart)"
    echo "  -l, --logs                 View logs from containers"
    echo
    echo "Examples:"
    echo "  $0 -a                      Pull, build, and restart"
    echo "  $0 -p -r                   Pull and restart without rebuilding"
    echo "  $0 -l                      View logs"
    echo
}

# Function to pull latest changes from GitHub
function pull_changes {
    echo "Pulling latest changes from GitHub..."
    cd $REPO_DIR
    git fetch
    git checkout $BRANCH
    git pull origin $BRANCH
    echo "Done."
    echo
}

# Function to rebuild Docker containers
function build_containers {
    echo "Rebuilding Docker containers..."
    cd $REPO_DIR
    docker-compose -f $DOCKER_COMPOSE_FILE build
    echo "Done."
    echo
}

# Function to restart Docker containers
function restart_containers {
    echo "Restarting Docker containers..."
    cd $REPO_DIR
    docker-compose -f $DOCKER_COMPOSE_FILE down
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    echo "Done."
    echo
}

# Function to view logs
function view_logs {
    echo "Viewing logs from containers..."
    cd $REPO_DIR
    docker-compose -f $DOCKER_COMPOSE_FILE logs -f
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_usage
    exit 0
fi

while [ "$1" != "" ]; do
    case $1 in
        -h | --help )           show_usage
                                exit 0
                                ;;
        -p | --pull )           pull_changes
                                ;;
        -b | --build )          build_containers
                                ;;
        -r | --restart )        restart_containers
                                ;;
        -a | --all )            pull_changes
                                build_containers
                                restart_containers
                                ;;
        -l | --logs )           view_logs
                                ;;
        * )                     show_usage
                                exit 1
    esac
    shift
done

echo "All operations completed."
