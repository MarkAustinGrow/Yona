import requests
import json
import sseclient
import threading
import time
import logging
import uuid

class CoralClient:
    def __init__(self, session_id=None, app_id="default-app", privacy_key="public", server_url="http://coral.pushcollective.club:3001"):
        """
        Initialize the Coral Protocol client.
        
        Args:
            session_id (str, optional): Unique session identifier. Defaults to a generated ID.
            app_id (str, optional): Application ID. Defaults to "default-app".
            privacy_key (str, optional): Privacy key. Defaults to "public".
            server_url (str, optional): Base URL of the Coral server. Defaults to "http://coral.pushcollective.club:3001".
        """
        self.session_id = session_id or f"yona-agent-{uuid.uuid4().hex[:8]}"
        self.app_id = app_id
        self.privacy_key = privacy_key
        self.base_url = server_url
        self.sse_url = f"{self.base_url}/{self.app_id}/{self.privacy_key}/{self.session_id}/sse"
        self.agent_id = None
        self.event_handlers = {}
        self.logger = logging.getLogger("coral_client")
        
        # Set up logging
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info(f"Initialized Coral client with session ID: {self.session_id}")
        self.logger.info(f"SSE URL: {self.sse_url}")
    
    def _send_tool_call(self, tool, args):
        """
        Send a tool call to the Coral server.
        
        Args:
            tool (str): The tool name to call.
            args (dict): The arguments for the tool.
            
        Returns:
            dict: The response from the server, or None if the request failed.
        """
        message = {
            "type": "tool_call",
            "tool": tool,
            "args": args
        }
        
        self.logger.info(f"Sending tool call: {tool}")
        self.logger.debug(f"Tool call details: {json.dumps(message)}")
        
        try:
            # Try sending the tool call to the SSE endpoint
            response = requests.post(
                self.sse_url,
                headers={"Content-Type": "application/json"},
                json=message
            )
            
            self.logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.logger.debug(f"Tool call response: {json.dumps(result)}")
                    return result
                except json.JSONDecodeError:
                    self.logger.error(f"Response is not JSON: {response.text}")
                    return None
            else:
                self.logger.error(f"Error sending tool call: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Exception sending tool call: {str(e)}")
            return None
    
    def register_agent(self, name, description):
        """
        Register an agent with the Coral server.
        
        Args:
            name (str): The name of the agent.
            description (str): A description of the agent.
            
        Returns:
            str: The agent ID assigned by the server, or None if registration failed.
        """
        self.logger.info(f"Registering agent: {name}")
        
        response = self._send_tool_call("register_agent", {
            "name": name,
            "description": description
        })
        
        if response and response.get("type") == "tool_response" and response.get("tool") == "register_agent":
            self.agent_id = response["result"]["agent_id"]
            self.logger.info(f"Agent registered with ID: {self.agent_id}")
            return self.agent_id
        else:
            self.logger.error(f"Failed to register agent: {response}")
            return None
    
    def list_agents(self):
        """
        List all registered agents.
        
        Returns:
            list: A list of agent information dictionaries, or None if the request failed.
        """
        self.logger.info("Listing agents")
        
        response = self._send_tool_call("list_agents", {})
        
        if response and response.get("type") == "tool_response" and response.get("tool") == "list_agents":
            agents = response["result"]["agents"]
            self.logger.info(f"Retrieved {len(agents)} agents")
            return agents
        else:
            self.logger.error(f"Failed to list agents: {response}")
            return None
    
    def create_thread(self, participants, metadata=None):
        """
        Create a new thread.
        
        Args:
            participants (list): List of agent IDs to include in the thread.
            metadata (dict, optional): Additional metadata for the thread.
            
        Returns:
            str: The thread ID assigned by the server, or None if the request failed.
        """
        self.logger.info(f"Creating thread with {len(participants)} participants")
        
        response = self._send_tool_call("create_thread", {
            "participants": participants,
            "metadata": metadata or {}
        })
        
        if response and response.get("type") == "tool_response" and response.get("tool") == "create_thread":
            thread_id = response["result"]["thread_id"]
            self.logger.info(f"Thread created with ID: {thread_id}")
            return thread_id
        else:
            self.logger.error(f"Failed to create thread: {response}")
            return None
    
    def send_message(self, thread_id, content, mentions=None):
        """
        Send a message to a thread.
        
        Args:
            thread_id (str): The ID of the thread to send the message to.
            content (str): The content of the message.
            mentions (list, optional): List of agent IDs to mention.
            
        Returns:
            str: The message ID assigned by the server, or None if the request failed.
        """
        self.logger.info(f"Sending message to thread: {thread_id}")
        
        response = self._send_tool_call("send_message", {
            "thread_id": thread_id,
            "content": content,
            "mentions": mentions or []
        })
        
        if response and response.get("type") == "tool_response" and response.get("tool") == "send_message":
            message_id = response["result"]["message_id"]
            self.logger.info(f"Message sent with ID: {message_id}")
            return message_id
        else:
            self.logger.error(f"Failed to send message: {response}")
            return None
    
    def wait_for_mentions(self, agent_id, timeout_seconds=60):
        """
        Wait for mentions of the specified agent.
        
        Args:
            agent_id (str): The ID of the agent to wait for mentions of.
            timeout_seconds (int, optional): Maximum time to wait in seconds.
            
        Returns:
            list: A list of messages mentioning the agent, or None if the request failed.
        """
        self.logger.info(f"Waiting for mentions of agent: {agent_id}")
        
        response = self._send_tool_call("wait_for_mentions", {
            "agent_id": agent_id,
            "timeout_seconds": timeout_seconds
        })
        
        if response and response.get("type") == "tool_response" and response.get("tool") == "wait_for_mentions":
            messages = response["result"]["messages"]
            self.logger.info(f"Received {len(messages)} mentions")
            return messages
        else:
            self.logger.error(f"Failed to wait for mentions: {response}")
            return None
    
    def start_listening(self, event_handlers=None):
        """
        Start listening for events from the Coral server.
        
        Args:
            event_handlers (dict, optional): Dictionary mapping event types to handler functions.
            
        Returns:
            threading.Thread: The thread that is listening for events.
        """
        if event_handlers:
            self.event_handlers.update(event_handlers)
        
        def _listen():
            self.logger.info(f"Starting event listener for session: {self.session_id}")
            headers = {"Accept": "text/event-stream"}
            
            while True:
                try:
                    self.logger.info(f"Connecting to SSE endpoint: {self.sse_url}")
                    response = requests.get(self.sse_url, headers=headers, stream=True)
                    
                    if response.status_code == 200:
                        self.logger.info("SSE connection established successfully")
                        client = sseclient.SSEClient(response)
                        
                        for event in client.events():
                            try:
                                self.logger.debug(f"Received event: {event.data}")
                                data = json.loads(event.data)
                                event_type = data.get("type")
                                
                                if event_type in self.event_handlers:
                                    self.logger.info(f"Processing event of type: {event_type}")
                                    self.event_handlers[event_type](data)
                                else:
                                    self.logger.debug(f"No handler for event type: {event_type}")
                            except Exception as e:
                                self.logger.error(f"Error processing event: {str(e)}")
                    else:
                        self.logger.error(f"Failed to connect to SSE endpoint: {response.status_code} - {response.text}")
                        time.sleep(5)  # Wait before retrying
                except Exception as e:
                    self.logger.error(f"Error in event listener: {str(e)}")
                    time.sleep(5)  # Wait before retrying
        
        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()
        self.logger.info("Event listener thread started")
        return thread

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a client
    client = CoralClient()
    
    # Define event handlers
    def handle_tool_response(data):
        print(f"Received tool response: {json.dumps(data, indent=2)}")
    
    def handle_message(data):
        print(f"Received message: {json.dumps(data, indent=2)}")
    
    # Start listening for events
    client.start_listening({
        "tool_response": handle_tool_response,
        "message": handle_message
    })
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
