#!/bin/bash
# Script to revert to the NuroAPI branch on the Linode server and rebuild Docker containers

# Set variables
SERVER_IP="172-236-28-244"
SERVER_USER="root"
REPO_DIR="/opt/yona"
BRANCH="NuroAPI"

# Display header
echo "====================================================="
echo "Yona Revert to NuroAPI Branch Script"
echo "====================================================="
echo

# Function to display usage
function show_usage {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -r, --revert               Revert to NuroAPI branch on the server"
    echo "  -b, --build                Rebuild Docker containers"
    echo "  -s, --restart              Restart Docker containers"
    echo "  -a, --all                  Perform all actions (revert, build, restart)"
    echo "  -l, --logs                 View logs from containers"
    echo
    echo "Examples:"
    echo "  $0 -a                      Revert, build, and restart"
    echo "  $0 -r -s                   Revert and restart without rebuilding"
    echo "  $0 -l                      View logs"
    echo
}

# Function to revert to NuroAPI branch on the server
function revert_to_nuroapi {
    echo "Reverting to NuroAPI branch on the server..."
    ssh $SERVER_USER@$SERVER_IP "cd $REPO_DIR && git fetch && git checkout $BRANCH && git pull origin $BRANCH"
    echo "Done."
    echo
}

# Function to rebuild Docker containers
function build_containers {
    echo "Rebuilding Docker containers..."
    ssh $SERVER_USER@$SERVER_IP "cd $REPO_DIR && docker-compose build"
    echo "Done."
    echo
}

# Function to restart Docker containers
function restart_containers {
    echo "Restarting Docker containers..."
    ssh $SERVER_USER@$SERVER_IP "cd $REPO_DIR && docker-compose down && docker-compose up -d"
    echo "Done."
    echo
}

# Function to view logs
function view_logs {
    echo "Viewing logs from containers..."
    ssh $SERVER_USER@$SERVER_IP "cd $REPO_DIR && docker-compose logs -f"
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
        -r | --revert )         revert_to_nuroapi
                                ;;
        -b | --build )          build_containers
                                ;;
        -s | --restart )        restart_containers
                                ;;
        -a | --all )            revert_to_nuroapi
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
