# Angus Communication Tests

This document provides instructions for testing communication with agent Angus using the Coral protocol.

## Overview

We've created four different test scripts to attempt communication with agent Angus:

1. **test_angus_communication.py**: Basic test using YonaAgentWithCoral
2. **test_angus_simple.py**: Simplified test using SimpleCoralAgent
3. **test_angus_enhanced.py**: Enhanced test with detailed logging
4. **test_angus_multiple_ids.py**: Tests multiple possible agent IDs for Angus

Each script attempts to:
- Connect to the Coral server
- Register an agent
- Create a thread with Angus (using ID `did:web:angus.ai`)
- Send a message to Angus
- Wait for a response

## Running the Tests

### Local Testing

To run the tests locally:

```bash
# Basic test
python test_angus_communication.py

# Simple test
python test_angus_simple.py

# Enhanced test
python test_angus_enhanced.py

# Multiple IDs test
python test_angus_multiple_ids.py
```

### Server Testing

You can use the provided shell script to run the tests on the Linode server:

```bash
# Make the script executable
chmod +x run_angus_tests.sh

# Show usage information
./run_angus_tests.sh --help

# Copy all test scripts to the server
./run_angus_tests.sh --copy

# Run the enhanced test
./run_angus_tests.sh --enhanced

# Run all tests
./run_angus_tests.sh --all

# View logs from the container
./run_angus_tests.sh --logs
```

Alternatively, you can run the tests manually:

```bash
# Copy the test scripts to the server
scp test_angus_*.py root@172-236-28-244:/opt/yona/

# SSH to the server
ssh root@172-236-28-244

# Navigate to the Yona directory
cd /opt/yona

# Copy the test script into the Docker container
docker cp test_angus_enhanced.py yona_yona-coral_1:/app/

# Run the test inside the Docker container
docker exec -it yona_yona-coral_1 python test_angus_enhanced.py
```

## Understanding the Results

Each test script creates detailed logs that can help diagnose communication issues:

- **test_angus_communication.py**: Logs to `angus_communication_test.log`
- **test_angus_simple.py**: Logs to `angus_simple_test.log`
- **test_angus_enhanced.py**: Logs to `angus_enhanced_test.log`
- **test_angus_multiple_ids.py**: Logs to `angus_multiple_ids_test.log`

You can also view the Docker container logs:

```bash
docker logs -f yona_yona-coral_1
```

## Troubleshooting

If communication with Angus fails, check the following:

1. **Agent ID**: Verify if `did:web:angus.ai` is the correct ID for agent Angus
2. **Coral Server**: Ensure the Coral server is running and accessible
3. **Message Format**: Check if the messages follow the required JSON-RPC format
4. **Thread Creation**: Verify that threads are being created successfully
5. **Mentions**: Ensure that mentions are properly formatted

## Alternative Agent IDs

If `did:web:angus.ai` doesn't work, the `test_angus_multiple_ids.py` script automatically tries these alternative formats:

- `angus`
- `agent_angus`
- `did:web:agent:angus`
- `angus_ai`
- `angus.ai`

You can also manually modify any of the test scripts to try different agent IDs:

```python
# Change this line in any of the test scripts
angus_id = "alternative_id_here"
```

To add more IDs to the multiple IDs test, edit the `angus_ids` list in `test_angus_multiple_ids.py`:

```python
# List of possible Angus IDs to try
angus_ids = [
    "did:web:angus.ai",
    "angus",
    "agent_angus",
    # Add more IDs here
]
```

## Next Steps

After running the tests, analyze the logs to determine:

1. If connection to the Coral server is successful
2. If agent registration is successful
3. If thread creation is successful
4. If message sending is successful
5. If any responses are received from Angus

Based on the results, you can make further adjustments to the communication approach.
