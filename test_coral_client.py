import requests
import json
import sseclient
import time
import argparse
import threading
import logging
import sys
import signal

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("coral_test")

# Global variables
exit_event = threading.Event()
agent_id = None
thread_id = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Shutting down...")
    exit_event.set()
    sys.exit(0)

def send_tool_call(url, tool, args):
    """Send a tool call to the Coral server"""
    message = {
        "type": "tool_call",
        "tool": tool,
        "args": args
    }
    
    logger.info(f"Sending tool call: {tool}")
    logger.debug(f"Tool call details: {json.dumps(message, indent=2)}")
    
    try:
        response = requests.post(
            url, 
            headers={"Content-Type": "application/json"},
            json=message,
            timeout=10
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                logger.debug(f"Response: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError:
                logger.error(f"Response is not JSON: {response.text}")
                return None
        else:
            logger.error(f"Error sending tool call: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {str(e)}")
        return None

def register_agent(url, name, description):
    """Register an agent with the Coral server"""
    logger.info(f"Registering agent: {name}")
    
    response = send_tool_call(url, "register_agent", {
        "name": name,
        "description": description
    })
    
    if response and response.get("type") == "tool_response" and response.get("tool") == "register_agent":
        agent_id = response["result"]["agent_id"]
        logger.info(f"✅ Agent registered with ID: {agent_id}")
        return agent_id
    else:
        logger.error(f"Failed to register agent: {response}")
        return None

def list_agents(url):
    """List all registered agents"""
    logger.info("Listing agents")
    
    response = send_tool_call(url, "list_agents", {})
    
    if response and response.get("type") == "tool_response" and response.get("tool") == "list_agents":
        agents = response["result"]["agents"]
        logger.info(f"Retrieved {len(agents)} agents:")
        for agent in agents:
            logger.info(f"  - {agent['name']} ({agent['agent_id']})")
        return agents
    else:
        logger.error(f"Failed to list agents: {response}")
        return None

def create_thread(url, participants, metadata=None):
    """Create a new thread"""
    logger.info(f"Creating thread with {len(participants)} participants")
    
    response = send_tool_call(url, "create_thread", {
        "participants": participants,
        "metadata": metadata or {}
    })
    
    if response and response.get("type") == "tool_response" and response.get("tool") == "create_thread":
        thread_id = response["result"]["thread_id"]
        logger.info(f"✅ Thread created with ID: {thread_id}")
        return thread_id
    else:
        logger.error(f"Failed to create thread: {response}")
        return None

def send_message(url, thread_id, content, mentions=None):
    """Send a message to a thread"""
    logger.info(f"Sending message to thread: {thread_id}")
    
    response = send_tool_call(url, "send_message", {
        "thread_id": thread_id,
        "content": content,
        "mentions": mentions or []
    })
    
    if response and response.get("type") == "tool_response" and response.get("tool") == "send_message":
        message_id = response["result"]["message_id"]
        logger.info(f"✅ Message sent with ID: {message_id}")
        return message_id
    else:
        logger.error(f"Failed to send message: {response}")
        return None

def wait_for_mentions(url, agent_id, timeout_seconds=30):
    """Wait for mentions of the specified agent"""
    logger.info(f"Waiting for mentions of agent: {agent_id}")
    
    response = send_tool_call(url, "wait_for_mentions", {
        "agent_id": agent_id,
        "timeout_seconds": timeout_seconds
    })
    
    if response and response.get("type") == "tool_response" and response.get("tool") == "wait_for_mentions":
        messages = response["result"]["messages"]
        logger.info(f"Received {len(messages)} mentions")
        for message in messages:
            logger.info(f"  - From: {message['sender_id']}, Content: {message['content']}")
        return messages
    else:
        logger.error(f"Failed to wait for mentions: {response}")
        return None

def event_listener(sse_url):
    """Listen for events from the Coral server"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Starting event listener for: {sse_url}")
    
    try:
        response = requests.get(sse_url, headers=headers, stream=True)
        
        if response.status_code != 200:
            logger.error(f"Error connecting to server: {response.status_code} {response.reason}")
            logger.error(f"Response: {response.text}")
            return
            
        client = sseclient.SSEClient(response)
        logger.info("SSE connection established successfully")
        
        for event in client.events():
            if exit_event.is_set():
                break
                
            logger.debug(f"Received event: {event.data}")
            
            try:
                data = json.loads(event.data)
                event_type = data.get("type")
                
                if event_type == "tool_response":
                    tool = data.get("tool")
                    logger.info(f"Received tool response for: {tool}")
                    
                    # Process specific tool responses
                    if tool == "register_agent":
                        global agent_id
                        agent_id = data.get("result", {}).get("agent_id")
                        if agent_id:
                            logger.info(f"✅ Agent ID from event: {agent_id}")
                    
                    elif tool == "create_thread":
                        global thread_id
                        thread_id = data.get("result", {}).get("thread_id")
                        if thread_id:
                            logger.info(f"✅ Thread ID from event: {thread_id}")
                
                elif event_type == "message":
                    logger.info(f"Received message: {data.get('content')}")
                    logger.info(f"From: {data.get('sender_id')}")
                    logger.info(f"Thread: {data.get('thread_id')}")
                    
                else:
                    logger.info(f"Received event of type: {event_type}")
                    
            except json.JSONDecodeError:
                logger.error("Error parsing event data as JSON")
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception in event listener: {str(e)}")
    except Exception as e:
        logger.error(f"Error in event listener: {str(e)}")

def run_interactive_mode(base_url, sse_url):
    """Run an interactive test session"""
    global agent_id, thread_id
    
    logger.info("\n=== Interactive Mode ===")
    logger.info("Type 'help' for available commands")
    
    # Start the event listener in a separate thread
    listener_thread = threading.Thread(target=event_listener, args=(sse_url,), daemon=True)
    listener_thread.start()
    
    while not exit_event.is_set():
        try:
            command = input("\nCommand: ").strip()
            
            if command == "exit" or command == "quit":
                logger.info("Exiting interactive mode")
                exit_event.set()
                break
                
            elif command == "help":
                print("\nAvailable commands:")
                print("  register - Register a new agent")
                print("  list - List all registered agents")
                print("  create - Create a new thread")
                print("  send - Send a message to a thread")
                print("  wait - Wait for mentions")
                print("  status - Show current agent and thread IDs")
                print("  exit/quit - Exit the program")
                
            elif command == "register":
                name = input("Agent name: ").strip()
                description = input("Agent description: ").strip()
                agent_id = register_agent(base_url, name, description)
                
            elif command == "list":
                list_agents(base_url)
                
            elif command == "create":
                if not agent_id:
                    logger.error("No agent ID available. Register an agent first.")
                    continue
                    
                participants = input("Participants (comma-separated agent IDs, leave empty for current agent only): ").strip()
                if participants:
                    participant_list = [p.strip() for p in participants.split(",")]
                else:
                    participant_list = [agent_id]
                    
                topic = input("Thread topic: ").strip()
                metadata = {"topic": topic} if topic else {}
                
                thread_id = create_thread(base_url, participant_list, metadata)
                
            elif command == "send":
                if not thread_id:
                    logger.error("No thread ID available. Create a thread first.")
                    continue
                    
                content = input("Message content: ").strip()
                mentions = input("Mentions (comma-separated agent IDs, leave empty for none): ").strip()
                mention_list = [m.strip() for m in mentions.split(",")] if mentions else []
                
                send_message(base_url, thread_id, content, mention_list)
                
            elif command == "wait":
                if not agent_id:
                    logger.error("No agent ID available. Register an agent first.")
                    continue
                    
                timeout = input("Timeout in seconds (default: 30): ").strip()
                timeout = int(timeout) if timeout else 30
                
                wait_for_mentions(base_url, agent_id, timeout)
                
            elif command == "status":
                logger.info(f"Current agent ID: {agent_id or 'None'}")
                logger.info(f"Current thread ID: {thread_id or 'None'}")
                
            else:
                logger.error(f"Unknown command: {command}")
                
        except KeyboardInterrupt:
            logger.info("\nExiting interactive mode")
            exit_event.set()
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")

def run_automated_test(base_url, sse_url, agent_name):
    """Run an automated test sequence"""
    global agent_id, thread_id
    
    logger.info("\n=== Automated Test Mode ===")
    
    # Start the event listener in a separate thread
    listener_thread = threading.Thread(target=event_listener, args=(sse_url,), daemon=True)
    listener_thread.start()
    
    try:
        # Step 1: Register an agent
        logger.info("\nStep 1: Register an agent")
        agent_id = register_agent(base_url, agent_name, f"Test agent for {agent_name}")
        if not agent_id:
            logger.error("Failed to register agent. Exiting test.")
            return
        
        time.sleep(1)
        
        # Step 2: List all agents
        logger.info("\nStep 2: List all agents")
        agents = list_agents(base_url)
        if not agents:
            logger.error("Failed to list agents. Continuing test.")
        
        time.sleep(1)
        
        # Step 3: Create a thread
        logger.info("\nStep 3: Create a thread")
        thread_id = create_thread(base_url, [agent_id], {"topic": "Automated test thread"})
        if not thread_id:
            logger.error("Failed to create thread. Exiting test.")
            return
        
        time.sleep(1)
        
        # Step 4: Send a message to the thread
        logger.info("\nStep 4: Send a message to the thread")
        message_id = send_message(base_url, thread_id, "Hello from the automated test!", [agent_id])
        if not message_id:
            logger.error("Failed to send message. Exiting test.")
            return
        
        time.sleep(1)
        
        # Step 5: Wait for mentions
        logger.info("\nStep 5: Wait for mentions")
        messages = wait_for_mentions(base_url, agent_id, 10)
        
        # Step 6: Test complete
        logger.info("\n✅ Automated test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in automated test: {e}")
    
    # Keep running for a bit to receive any pending events
    logger.info("\nWaiting for 5 seconds to receive any pending events...")
    time.sleep(5)

def main():
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test client for Coral server')
    parser.add_argument('--server', default='coral.pushcollective.club', help='Coral server hostname')
    parser.add_argument('--port', default='443', help='Coral server port')
    parser.add_argument('--app', default='default-app', help='Application ID')
    parser.add_argument('--key', default='public', help='Privacy key')
    parser.add_argument('--session', default=f'test-session-{int(time.time())}', help='Session ID')
    parser.add_argument('--protocol', default='https', choices=['http', 'https'], help='Protocol (http or https)')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--agent-name', default='TestAgent', help='Name for the test agent')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Construct the URLs
    base_url = f"{args.protocol}://{args.server}"
    if args.port != '80' and args.port != '443':
        base_url += f":{args.port}"
    base_url += f"/{args.app}/{args.key}/{args.session}"
    sse_url = f"{base_url}/sse"
    
    logger.info(f"Base URL: {base_url}")
    logger.info(f"SSE URL: {sse_url}")
    
    # Run in interactive or automated mode
    if args.interactive:
        run_interactive_mode(base_url, sse_url)
    else:
        run_automated_test(base_url, sse_url, args.agent_name)

if __name__ == "__main__":
    main()
