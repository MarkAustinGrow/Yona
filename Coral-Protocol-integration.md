✅ Step-by-Step Integration Plan for Yona Agent into Coral Protocol
Goal:
Integrate the existing Yona AI music agent with the Coral Protocol, enabling it to register, communicate, coordinate tasks, and respond to mentions with other AI agents through the Coral Server.

🚩 Step 1: Setup and Initial Client Integration
Tasks:
Install the required Python libraries:

```bash
pip install requests sseclient-py
```

Initialize SSE Client: Create a small script (coral_client_setup.py) to verify client connection:

```python
import requests
import json
import sseclient

# Define the session ID - this should be unique for your agent
session_id = "yona-agent-session"

# Connect to the Coral server
url = f"https://coral.pushcollective.club/default-app/public/{session_id}/sse"
headers = {"Accept": "text/event-stream"}
response = requests.get(url, headers=headers, stream=True)
client = sseclient.SSEClient(response)

print("SSE client initialized successfully.")

# Test the connection by listening for a few events
for event in client.events():
    print(f"Received event: {event.data}")
    # Break after receiving a few events to avoid an infinite loop
    break

print("Connection test completed.")
```

Confirm the client connects successfully to the Coral Server.

🚩 Step 2: Create a CoralClient Class
Tasks:
Create a wrapper class for the Coral Protocol client:

```python
import requests
import json
import sseclient
import threading
import time
import logging

class CoralClient:
    def __init__(self, session_id=None, app_id="default-app", privacy_key="public"):
        """
        Initialize the Coral Protocol client.
        
        Args:
            session_id (str, optional): Unique session identifier. Defaults to a generated ID.
            app_id (str, optional): Application ID. Defaults to "default-app".
            privacy_key (str, optional): Privacy key. Defaults to "public".
        """
        self.session_id = session_id or f"yona-agent-{int(time.time())}"
        self.app_id = app_id
        self.privacy_key = privacy_key
        self.base_url = "https://coral.pushcollective.club"
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
    
    def _send_tool_call(self, tool, args):
        """
        Send a tool call to the Coral server.
        
        Args:
            tool (str): The tool name to call.
            args (dict): The arguments for the tool.
            
        Returns:
            dict: The response from the server.
        """
        message = {
            "type": "tool_call",
            "tool": tool,
            "args": args
        }
        
        self.logger.info(f"Sending tool call: {tool}")
        self.logger.debug(f"Tool call details: {json.dumps(message)}")
        
        response = requests.post(
            self.sse_url,
            headers={"Content-Type": "application/json"},
            json=message
        )
        
        if response.status_code != 200:
            self.logger.error(f"Error sending tool call: {response.status_code} - {response.text}")
            raise Exception(f"Error sending tool call: {response.status_code} - {response.text}")
        
        result = response.json()
        self.logger.debug(f"Tool call response: {json.dumps(result)}")
        return result
    
    def register_agent(self, name, description):
        """
        Register an agent with the Coral server.
        
        Args:
            name (str): The name of the agent.
            description (str): A description of the agent.
            
        Returns:
            str: The agent ID assigned by the server.
        """
        response = self._send_tool_call("register_agent", {
            "name": name,
            "description": description
        })
        
        if response.get("type") == "tool_response" and response.get("tool") == "register_agent":
            self.agent_id = response["result"]["agent_id"]
            self.logger.info(f"Agent registered with ID: {self.agent_id}")
            return self.agent_id
        else:
            self.logger.error(f"Failed to register agent: {response}")
            raise Exception(f"Failed to register agent: {response}")
    
    def list_agents(self):
        """
        List all registered agents.
        
        Returns:
            list: A list of agent information dictionaries.
        """
        response = self._send_tool_call("list_agents", {})
        
        if response.get("type") == "tool_response" and response.get("tool") == "list_agents":
            agents = response["result"]["agents"]
            self.logger.info(f"Retrieved {len(agents)} agents")
            return agents
        else:
            self.logger.error(f"Failed to list agents: {response}")
            raise Exception(f"Failed to list agents: {response}")
    
    def create_thread(self, participants, metadata=None):
        """
        Create a new thread.
        
        Args:
            participants (list): List of agent IDs to include in the thread.
            metadata (dict, optional): Additional metadata for the thread.
            
        Returns:
            str: The thread ID assigned by the server.
        """
        response = self._send_tool_call("create_thread", {
            "participants": participants,
            "metadata": metadata or {}
        })
        
        if response.get("type") == "tool_response" and response.get("tool") == "create_thread":
            thread_id = response["result"]["thread_id"]
            self.logger.info(f"Thread created with ID: {thread_id}")
            return thread_id
        else:
            self.logger.error(f"Failed to create thread: {response}")
            raise Exception(f"Failed to create thread: {response}")
    
    def send_message(self, thread_id, content, mentions=None):
        """
        Send a message to a thread.
        
        Args:
            thread_id (str): The ID of the thread to send the message to.
            content (str): The content of the message.
            mentions (list, optional): List of agent IDs to mention.
            
        Returns:
            str: The message ID assigned by the server.
        """
        response = self._send_tool_call("send_message", {
            "thread_id": thread_id,
            "content": content,
            "mentions": mentions or []
        })
        
        if response.get("type") == "tool_response" and response.get("tool") == "send_message":
            message_id = response["result"]["message_id"]
            self.logger.info(f"Message sent with ID: {message_id}")
            return message_id
        else:
            self.logger.error(f"Failed to send message: {response}")
            raise Exception(f"Failed to send message: {response}")
    
    def wait_for_mentions(self, agent_id, timeout_seconds=60):
        """
        Wait for mentions of the specified agent.
        
        Args:
            agent_id (str): The ID of the agent to wait for mentions of.
            timeout_seconds (int, optional): Maximum time to wait in seconds.
            
        Returns:
            list: A list of messages mentioning the agent.
        """
        response = self._send_tool_call("wait_for_mentions", {
            "agent_id": agent_id,
            "timeout_seconds": timeout_seconds
        })
        
        if response.get("type") == "tool_response" and response.get("tool") == "wait_for_mentions":
            messages = response["result"]["messages"]
            self.logger.info(f"Received {len(messages)} mentions")
            return messages
        else:
            self.logger.error(f"Failed to wait for mentions: {response}")
            raise Exception(f"Failed to wait for mentions: {response}")
    
    def start_listening(self, event_handlers=None):
        """
        Start listening for events from the Coral server.
        
        Args:
            event_handlers (dict, optional): Dictionary mapping event types to handler functions.
        """
        if event_handlers:
            self.event_handlers.update(event_handlers)
        
        def _listen():
            headers = {"Accept": "text/event-stream"}
            response = requests.get(self.sse_url, headers=headers, stream=True)
            client = sseclient.SSEClient(response)
            
            self.logger.info("Started listening for events")
            
            for event in client.events():
                try:
                    data = json.loads(event.data)
                    event_type = data.get("type")
                    
                    self.logger.debug(f"Received event: {event.data}")
                    
                    if event_type in self.event_handlers:
                        self.event_handlers[event_type](data)
                    
                except Exception as e:
                    self.logger.error(f"Error processing event: {str(e)}")
        
        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()
        return thread
```

Test the CoralClient class with a simple script:

```python
from coral_client import CoralClient

# Create a client
client = CoralClient(session_id="test-session")

# Register an agent
agent_id = client.register_agent(
    name="TestAgent",
    description="A test agent for the Coral Protocol"
)

print(f"Registered agent with ID: {agent_id}")

# List all agents
agents = client.list_agents()
print(f"Found {len(agents)} agents:")
for agent in agents:
    print(f"  - {agent['name']} ({agent['agent_id']})")
```

🚩 Step 3: Extend YonaAgent Class with Coral Client
Tasks:
Add Coral Client as a Dependency: Modify your YonaAgent class constructor to accept a Coral client:

```python
class YonaAgent:
    def __init__(self, openai_api_key=None, coral_client=None, ...):
        self.coral_client = coral_client
        # existing initialization logic
```

Initialize Yona with Coral Client:

```python
from coral_client import CoralClient

# Create a Coral client
coral_client = CoralClient(session_id="yona-agent-session")

# Initialize Yona with the Coral client
yona_agent = YonaAgent(openai_api_key="YOUR_OPENAI_KEY", coral_client=coral_client)
```

🚩 Step 4: Agent Registration with Coral Server
Tasks:
Implement Agent Registration Method:

```python
def register_with_coral(self):
    """
    Register the Yona agent with the Coral server.
    
    Returns:
        str: The agent ID assigned by the server.
    """
    if not self.coral_client:
        raise ValueError("Coral client not initialized")
    
    agent_id = self.coral_client.register_agent(
        name="YonaAgent",
        description="An AI music agent that creates songs based on prompts and feedback"
    )
    
    self.coral_agent_id = agent_id
    return agent_id
```

Test Agent Registration:

```python
# Register Yona with the Coral server
agent_id = yona_agent.register_with_coral()
print(f"Yona registered with Coral server. Agent ID: {agent_id}")
```

Confirm registration through Coral Server logs or by listing agents.

🚩 Step 5: Thread Management & Messaging
Tasks:
Create Helper Methods for Thread Management: Add methods to YonaAgent for interacting with Coral threads:

```python
def create_coral_thread(self, participants=None, metadata=None):
    """
    Create a new thread in the Coral server.
    
    Args:
        participants (list, optional): List of agent IDs to include in the thread.
                                      If None, only includes this agent.
        metadata (dict, optional): Additional metadata for the thread.
        
    Returns:
        str: The thread ID assigned by the server.
    """
    if not self.coral_client:
        raise ValueError("Coral client not initialized")
    
    if not hasattr(self, 'coral_agent_id'):
        raise ValueError("Agent not registered with Coral server")
    
    # Ensure this agent is included in participants
    if participants is None:
        participants = [self.coral_agent_id]
    elif self.coral_agent_id not in participants:
        participants.append(self.coral_agent_id)
    
    return self.coral_client.create_thread(participants, metadata)

def send_message(self, thread_id, content, mentions=None):
    """
    Send a message to a thread.
    
    Args:
        thread_id (str): The ID of the thread to send the message to.
        content (str): The content of the message.
        mentions (list, optional): List of agent IDs to mention.
        
    Returns:
        str: The message ID assigned by the server.
    """
    if not self.coral_client:
        raise ValueError("Coral client not initialized")
    
    return self.coral_client.send_message(thread_id, content, mentions)
```

Verify Thread Creation and Messaging:

Test creating a thread and sending a message manually:

```python
# Create a thread
thread_id = yona_agent.create_coral_thread()
print(f"Created thread with ID: {thread_id}")

# Send a message to the thread
message_id = yona_agent.send_message(thread_id, "Hello from Yona!")
print(f"Sent message with ID: {message_id}")
```

🚩 Step 6: Handling Mentions and Responding to Requests
Tasks:
Implement Mention Handling:

```python
def process_coral_requests(self, timeout_seconds=60):
    """
    Process mentions of this agent in the Coral server.
    
    Args:
        timeout_seconds (int, optional): Maximum time to wait for mentions.
        
    Returns:
        list: A list of processed message IDs.
    """
    if not self.coral_client:
        raise ValueError("Coral client not initialized")
    
    if not hasattr(self, 'coral_agent_id'):
        raise ValueError("Agent not registered with Coral server")
    
    # Wait for mentions
    mentions = self.coral_client.wait_for_mentions(
        self.coral_agent_id,
        timeout_seconds=timeout_seconds
    )
    
    processed_messages = []
    
    for mention in mentions:
        thread_id = mention["thread_id"]
        prompt = mention["content"]
        
        # Generate a song based on the prompt
        song_data = self.generate_song_concept(prompt)
        lyrics = self.generate_lyrics(song_data)
        song_result = self.create_song(title=song_data['title'], lyrics=lyrics)
        
        # Prepare the response message
        message = (f"Created song '{song_data['title']}'\n"
                  f"Audio: {song_result['audio_url']}\n"
                  f"Lyrics:\n{lyrics}")
        
        # Send the response
        message_id = self.send_message(thread_id, message)
        processed_messages.append(message_id)
    
    return processed_messages
```

Test Mention Handling:

Manually simulate mentions from other agents in the Coral Server and verify Yona responds properly.

🚩 Step 7: Integrating Feedback Processing with Coral
Tasks:
Implement Feedback Response via Coral: Add method for processing Coral feedback mentions:

```python
def handle_feedback_mention(self, feedback_message, original_song_id, thread_id):
    """
    Process feedback on a song and create an improved version.
    
    Args:
        feedback_message (str): The feedback message.
        original_song_id (str): The ID of the original song.
        thread_id (str): The ID of the thread to respond in.
        
    Returns:
        str: The message ID of the response.
    """
    # Modify parameters based on feedback
    modified_params = self.modify_parameters_with_openai(original_song_id, feedback_message)
    
    # Create an improved song
    song_result = self.create_song(**modified_params)
    
    # Send the response
    message = f"Created improved song: {song_result['audio_url']}"
    return self.send_message(thread_id, message)
```

Test Feedback Workflow:

Manually post feedback in a Coral thread and verify Yona generates and posts an improved song back to the thread.

🚩 Step 8: Create a Continuous Listening & Response Loop
Tasks:
Entry-point Script for Continuous Operation: Create a dedicated script (run_yona_coral.py) that continuously checks for mentions:

```python
from src.agent import YonaAgent
from coral_client import CoralClient
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("yona_coral.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("yona_coral")

def main():
    # Create a Coral client
    coral_client = CoralClient(session_id="yona-agent-session")
    
    # Initialize Yona with the Coral client
    yona = YonaAgent(openai_api_key="your-key", coral_client=coral_client)
    
    # Register Yona with the Coral server
    agent_id = yona.register_with_coral()
    logger.info(f"Yona registered with Coral. Agent ID: {agent_id}")
    logger.info("Awaiting mentions...")

    while True:
        try:
            # Process mentions
            processed = yona.process_coral_requests(timeout_seconds=30)
            if processed:
                logger.info(f"Processed {len(processed)} mentions")
            
            # Sleep briefly to avoid tight loops
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            # Sleep a bit longer after an error
            time.sleep(5)

if __name__ == "__main__":
    main()
```

Deploy and Monitor:

Deploy the continuous script and monitor its logs and interactions with the Coral Server.

🚩 Step 9: Monitoring, Error Handling, and Observability
Tasks:
Enhanced Logging and Monitoring:

- Log all Coral interactions with clear, structured log messages.
- Integrate Coral-related metrics into your existing monitoring dashboards.

Robust Error Handling:

- Ensure any exceptions or failures in Coral communication are explicitly logged and alerted.
- Implement retry logic for transient failures.
- Add circuit breakers for persistent failures.

🚩 Step 10: Deployment and Production-Ready Setup
Tasks:
Dockerize Coral Integration:

Update Dockerfile and docker-compose files to include Coral integration dependencies:

```dockerfile
# Add Coral dependencies
RUN pip install requests sseclient-py
```

Production Deployment:

- Deploy to staging first; thoroughly test Coral interactions.
- Deploy to production, monitoring closely.

✅ Final Integration Checklist:

| Step | Task | Completion Criteria | Status |
|------|------|---------------------|--------|
| 1 | Client Setup | SSE client successfully connects | ☐ |
| 2 | CoralClient Class | CoralClient class implemented and tested | ☐ |
| 3 | Extend YonaAgent | YonaAgent initialized with Coral client | ☐ |
| 4 | Agent Registration | Yona registers successfully | ☐ |
| 5 | Thread & Messaging | Threads created; messages sent properly | ☐ |
| 6 | Mention Handling | Yona responds correctly to mentions | ☐ |
| 7 | Feedback Integration | Yona integrates feedback workflow | ☐ |
| 8 | Continuous Integration Script | Continuous Coral listening operational | ☐ |
| 9 | Monitoring and Error Handling | Comprehensive logging & monitoring set | ☐ |
| 10 | Production Deployment | Coral integration deployed & monitored | ☐ |

✅ Recommended Approach:
- Follow this guide sequentially.
- Test thoroughly at the completion of each step before progressing.
- Maintain clear, documented commits for each stage of integration.

By following these ordered tasks, your Yona agent will seamlessly integrate with the Coral Protocol, ensuring smooth, reliable collaborative workflows with other AI agents.
