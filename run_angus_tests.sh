#!/bin/bash
# Script to run Angus communication tests on the Linode server

# Set variables
SERVER_IP="172-236-28-244"
SERVER_USER="root"
YONA_DIR="/opt/yona"
CONTAINER_NAME="yona_yona-coral_1"

# Display header
echo "====================================================="
echo "Angus Communication Tests Runner"
echo "====================================================="
echo

# Function to display usage
function show_usage {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -c, --copy                 Copy test scripts to server"
    echo "  -b, --basic                Run basic test"
    echo "  -s, --simple               Run simple test"
    echo "  -e, --enhanced             Run enhanced test"
    echo "  -m, --multiple-ids         Run multiple IDs test"
    echo "  -a, --all                  Run all tests"
    echo "  -l, --logs                 View logs from container"
    echo
    echo "Examples:"
    echo "  $0 -c -e                   Copy scripts and run enhanced test"
    echo "  $0 -a                      Run all tests"
    echo "  $0 -l                      View logs from container"
    echo
}

# Function to copy test scripts to server
function copy_scripts {
    echo "Copying test scripts to server..."
    scp test_angus_*.py $SERVER_USER@$SERVER_IP:$YONA_DIR/
    echo "Done."
    echo
}

# Function to run a test
function run_test {
    local test_script=$1
    local test_name=$2
    
    echo "Running $test_name test..."
    echo "Copying $test_script to container..."
    ssh $SERVER_USER@$SERVER_IP "cd $YONA_DIR && docker cp $test_script $CONTAINER_NAME:/app/"
    
    echo "Executing test in container..."
    ssh $SERVER_USER@$SERVER_IP "cd $YONA_DIR && docker exec -it $CONTAINER_NAME python $test_script"
    
    echo "Test completed."
    echo
}

# Function to view logs
function view_logs {
    echo "Viewing logs from container..."
    ssh $SERVER_USER@$SERVER_IP "cd $YONA_DIR && docker logs -f $CONTAINER_NAME"
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
        -c | --copy )           copy_scripts
                                ;;
        -b | --basic )          run_test "test_angus_communication.py" "basic"
                                ;;
        -s | --simple )         run_test "test_angus_simple.py" "simple"
                                ;;
        -e | --enhanced )       run_test "test_angus_enhanced.py" "enhanced"
                                ;;
        -m | --multiple-ids )   run_test "test_angus_multiple_ids.py" "multiple IDs"
                                ;;
        -a | --all )            copy_scripts
                                run_test "test_angus_communication.py" "basic"
                                run_test "test_angus_simple.py" "simple"
                                run_test "test_angus_enhanced.py" "enhanced"
                                run_test "test_angus_multiple_ids.py" "multiple IDs"
                                ;;
        -l | --logs )           view_logs
                                ;;
        * )                     show_usage
                                exit 1
    esac
    shift
done

echo "All operations completed."
