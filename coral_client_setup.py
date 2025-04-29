import requests
import json
import sseclient
import time
import threading

# Define the session ID - this should be unique for your agent
session_id = f"yona-agent-test-{int(time.time())}"
print(f"Using session ID: {session_id}")

# Connect to the Coral server
base_url = "https://coral.pushcollective.club"
sse_url = f"{base_url}/default-app/public/{session_id}/sse"
api_url = f"{base_url}/api"  # Try using a separate API endpoint for POST requests
message_url = f"{base_url}/default-app/public/{session_id}"  # Direct message URL without /sse
print(f"SSE URL: {sse_url}")
print(f"API URL: {api_url}")
print(f"Message URL: {message_url}")

# Start listening for events in a separate thread
def listen_for_events():
    headers = {"Accept": "text/event-stream"}
    try:
        print("Starting event listener...")
        response = requests.get(sse_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            client = sseclient.SSEClient(response)
            print("SSE client initialized successfully.")
            
            for event in client.events():
                print(f"Received event: {event.data}")
                # Don't break - keep listening for events
        else:
            print(f"Failed to connect listener. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error in event listener: {str(e)}")

# Start the listener thread
listener_thread = threading.Thread(target=listen_for_events, daemon=True)
listener_thread.start()

# Give the listener thread time to start
time.sleep(2)

# Try different endpoints for registration
def try_register_agent():
    endpoints = [
        message_url,  # Direct message URL (most likely to work)
        f"{api_url}/register_agent",
        f"{api_url}/agents",
        f"{base_url}/register_agent",
        f"{base_url}/agents",
        sse_url  # Original endpoint we tried
    ]
    
    message = {
        "type": "tool_call",
        "tool": "register_agent",
        "args": {
            "name": "YonaTestAgent",
            "description": "A test agent for the Coral Protocol"
        }
    }
    
    print(f"\nTrying to register agent with payload: {json.dumps(message)}")
    
    for endpoint in endpoints:
        try:
            print(f"\nTrying endpoint: {endpoint}")
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(message),
                timeout=5
            )
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"Registration response: {json.dumps(result, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    print(f"Response is not JSON: {response.text}")
            else:
                print(f"Failed with status code: {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    print("Could not get response text")
        except Exception as e:
            print(f"Error with endpoint {endpoint}: {str(e)}")
    
    return False

# Try to register the agent
success = try_register_agent()
if success:
    print("\nAgent registration successful!")
else:
    print("\nAgent registration failed with all endpoints.")

# Keep the script running for a while to receive events
print("\nKeeping connection open for 10 seconds to receive events...")
time.sleep(10)

print("\nTest completed.")
