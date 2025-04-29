#!/usr/bin/env python3
"""
Simple Coral Server Test Script (Fixed)

This script demonstrates the correct way to connect to a Coral server
and send tool calls using the JSON-RPC format.

Usage:
  python simple-coral-test-fixed.py [--server SERVER] [--http] [--devmode]

Options:
  --server SERVER  Server hostname (default: localhost:3001)
  --http           Use HTTP instead of HTTPS (default: True for localhost)
  --devmode        Use DevMode endpoints (default: True)
"""

import requests
import json
import time
import uuid
import re
import argparse
import sys
import threading
import queue
import subprocess

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple Coral Server Test Script')
    parser.add_argument('--server', default='localhost:3001', help='Server hostname')
    parser.add_argument('--http', action='store_true', help='Use HTTP instead of HTTPS')
    parser.add_argument('--devmode', action='store_true', help='Use DevMode endpoints')
    args = parser.parse_args()
    
    # Determine protocol (HTTP or HTTPS)
    protocol = "http" if args.http or args.server.startswith('localhost') else "https"
    
    # Determine if using devmode
    devmode_prefix = "/devmode" if args.devmode else ""
    
    # Create a unique session ID
    session_id = f"test-session-{int(time.time())}"
    agent_id = "test-agent"
    
    # Construct the URL
    base_url = f"{protocol}://{args.server}{devmode_prefix}/default-app/public/{session_id}"
    sse_url = f"{base_url}/sse?agentId={agent_id}"
    
    print(f"SSE URL: {sse_url}")
    
    # Queue to pass the transport session ID between threads
    session_id_queue = queue.Queue()
    
    # Function to capture the transport session ID from SSE events
    def capture_session_id():
        try:
            # Use requests to establish SSE connection
            headers = {"Accept": "text/event-stream"}
            response = requests.get(sse_url, headers=headers, stream=True)
            
            if response.status_code != 200:
                print(f"Error connecting to SSE endpoint: {response.status_code} {response.reason}")
                session_id_queue.put(None)
                return
                
            print("SSE connection established successfully")
            
            # Read the response line by line
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                    
                print(f"SSE: {line}")
                
                # Look for the endpoint event
                if line.strip() == "event: endpoint":
                    # The next line should contain the data with the session ID
                    data_line = next(response.iter_lines(decode_unicode=True), "").decode() if hasattr(next(response.iter_lines(decode_unicode=True), ""), 'decode') else next(response.iter_lines(decode_unicode=True), "")
                    print(f"SSE data: {data_line}")
                    
                    # Extract the session ID using regex
                    if data_line.startswith("data: "):
                        data_content = data_line[6:]  # Remove "data: " prefix
                        match = re.search(r'sessionId=([a-zA-Z0-9-]+)', data_content)
                        if match:
                            transport_session_id = match.group(1)
                            print(f"Found transport session ID: {transport_session_id}")
                            session_id_queue.put(transport_session_id)
                            return
                
                # Direct pattern match for sessionId in the line
                match = re.search(r'sessionId=([a-zA-Z0-9-]+)', line)
                if match:
                    transport_session_id = match.group(1)
                    print(f"Found transport session ID directly: {transport_session_id}")
                    session_id_queue.put(transport_session_id)
                    return
            
            print("Error: Could not find transport session ID in SSE events")
            session_id_queue.put(None)
        except Exception as e:
            print(f"Error in capture_session_id: {e}")
            session_id_queue.put(None)
    
    # Start the SSE connection in a separate thread
    print("\nConnecting to SSE endpoint...")
    sse_thread = threading.Thread(target=capture_session_id)
    sse_thread.daemon = True
    sse_thread.start()
    
    # Wait for the transport session ID
    print("Waiting for transport session ID...")
    try:
        transport_session_id = session_id_queue.get(timeout=10)
        if transport_session_id is None:
            print("Failed to get transport session ID")
            sys.exit(1)
            
        # Construct the message URL with the correct session ID
        message_url = f"{base_url}/message?sessionId={transport_session_id}"
        print(f"Message URL: {message_url}")
        
        # Register an agent using JSON-RPC format
        print("\nRegistering agent...")
        request_id = str(uuid.uuid4())
        register_message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tool_call",
            "params": {
                "tool": "register_agent",
                "args": {
                    "name": "YonaAgent",
                    "description": "An AI music agent that creates songs based on prompts and feedback"
                }
            }
        }
        
        print(f"Sending to {message_url}:")
        print(f"{json.dumps(register_message, indent=2)}")
        
        register_response = requests.post(
            message_url, 
            headers={"Content-Type": "application/json"},
            json=register_message
        )
        
        print(f"Response status: {register_response.status_code}")
        
        try:
            response_json = register_response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
            
            if register_response.status_code == 202 or register_response.status_code == 200:
                print("\n✅ Successfully sent register_agent request!")
                print("\nThe Coral server is working correctly!")
                
                # Extract agent_id from response if available
                if "result" in response_json and "agent_id" in response_json["result"]:
                    agent_id = response_json["result"]["agent_id"]
                    print(f"Registered agent with ID: {agent_id}")
            else:
                print("\n❌ Failed to register agent.")
                print("Please check the server logs for more information.")
        except:
            print(f"Response: {register_response.text}")
            
    except queue.Empty:
        print("Timeout waiting for transport session ID")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    print("Simple Coral Server Test Script (Fixed)")
    print("------------------------------")
    print("This script tests connectivity to a Coral server and verifies")
    print("that the server is working correctly.")
    print("")
    
    main()
