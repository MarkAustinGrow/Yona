# coral_client.py
import json
import uuid
import asyncio
import logging
import httpx
import sseclient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoralClient:
    def __init__(self, server_url, agent_id, session_id="session1"):
        self.server_url = server_url
        self.agent_id = agent_id
        self.session_id = session_id
        self.sse_url = f"{server_url}/devmode/exampleApplication/privkey/{session_id}/sse?agentId={self.agent_id}"
        self.client = httpx.AsyncClient()
        self.message_handlers = []
        self.transport_session_id = None
        self.connected = False
        self.pending_operations = []

    async def connect(self):
        """Connect to the Coral server via SSE."""
        logger.info(f"Connecting to Coral server at {self.sse_url}")
        try:
            response = self.client.stream('GET', self.sse_url)
            client = sseclient.SSEClient(response)
            
            # Process events in a separate task to avoid blocking
            async def process_events():
                for event in client.events():
                    if event.event == 'message':
                        try:
                            data = json.loads(event.data)
                            logger.info(f"Received SSE event: {data.get('type', 'unknown')}")
                            
                            # Extract transport_session_id if present
                            if 'transport_session_id' in data:
                                self.transport_session_id = data['transport_session_id']
                                logger.info(f"Received transport_session_id: {self.transport_session_id}")
                                self.connected = True
                                
                                # Process any pending operations
                                for operation in self.pending_operations:
                                    await operation()
                                self.pending_operations = []
                                
                            await self._handle_message(data)
                        except json.JSONDecodeError:
                            logger.error(f"Failed to decode SSE event data: {event.data}")
                        except Exception as e:
                            logger.error(f"Error processing SSE event: {str(e)}")
            
            # Start processing events
            asyncio.create_task(process_events())
            
        except Exception as e:
            logger.error(f"Error connecting to Coral server: {str(e)}")
            raise

    async def _handle_message(self, message):
        """Handle incoming messages from the Coral server."""
        for handler in self.message_handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {str(e)}")

    def add_message_handler(self, handler):
        """Add a handler for incoming messages."""
        self.message_handlers.append(handler)

    async def send_to_server(self, action, payload):
        """Send a message to the Coral server using the correct endpoint."""
        if not self.transport_session_id:
            logger.warning("Not connected to the server yet, queueing operation")
            
            # Queue the operation to be executed once connected
            future_operation = lambda: self.send_to_server(action, payload)
            self.pending_operations.append(future_operation)
            return None
            
        message_url = f"{self.server_url}/devmode/exampleApplication/privkey/{self.session_id}/message?sessionId={self.transport_session_id}"
        
        # Prepare the message with the action and payload
        message = {
            "action": action,
            "payload": payload
        }
        
        logger.info(f"Sending message to Coral server: {action}")
        try:
            response = await self.client.post(message_url, json=message)
            response_data = response.json()
            logger.info(f"Received response: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Error sending message to Coral server: {str(e)}")
            return {"error": str(e)}

    async def register_agent(self, name, description, capabilities=[]):
        """Register the agent with the Coral server."""
        logger.info(f"Registering agent {self.agent_id} with Coral server")
        payload = {
            "agent_id": self.agent_id,
            "name": name,
            "description": description,
            "capabilities": capabilities
        }
        
        response = await self.send_to_server("register_agent", payload)
        if response is None:
            logger.info(f"Registration operation queued for agent {self.agent_id}")
            return True  # Assume success for queued operations
        elif not response.get("error"):
            logger.info(f"Successfully registered agent {self.agent_id}")
            return True
        else:
            logger.error(f"Failed to register agent: {response.get('error', 'Unknown error')}")
            return False

    async def create_thread(self, participants, metadata={}):
        """Create a new thread with the specified participants."""
        logger.info(f"Creating thread with participants: {participants}")
        payload = {
            "participants": participants,
            "metadata": metadata
        }
        
        response = await self.send_to_server("create_thread", payload)
        if response is None:
            logger.info(f"Create thread operation queued")
            return "pending_thread_id"  # Return a placeholder ID for queued operations
        elif "thread_id" in response:
            thread_id = response.get("thread_id")
            logger.info(f"Created thread: {thread_id}")
            return thread_id
        else:
            logger.error(f"Failed to create thread: {response.get('error', 'Unknown error')}")
            return None

    async def send_message(self, thread_id, content, mentions=[], signature_info=None):
        """Send a message to a thread."""
        logger.info(f"Sending message to thread {thread_id}")
        
        # Prepare the message payload
        message_payload = {
            "thread_id": thread_id,
            "sender_id": self.agent_id,
            "content": content,
            "mentions": mentions
        }
        
        # Add signature information if provided
        if signature_info:
            message_payload["signature"] = signature_info.get("signature")
            message_payload["original_message"] = signature_info.get("message")
        
        response = await self.send_to_server("send_message", message_payload)
        if response is None:
            logger.info(f"Send message operation queued for thread {thread_id}")
            return {"status": "queued"}  # Return a status for queued operations
        elif not response.get("error"):
            logger.info(f"Successfully sent message to thread {thread_id}")
            return response
        else:
            logger.error(f"Failed to send message: {response.get('error', 'Unknown error')}")
            return {"error": response.get("error", "Unknown error")}
