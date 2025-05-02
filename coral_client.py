# coral_client.py
import json
import uuid
import asyncio
import logging
import httpx
import requests
import sseclient
import threading
import queue
import time

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
        self.sse_thread = None
        self.event_queue = queue.Queue()  # Thread-safe queue
        self.running = True

    async def connect(self):
        """Connect to the Coral server via SSE."""
        logger.info(f"Connecting to Coral server at {self.sse_url}")
        
        # Start SSE connection in a separate thread since it's blocking
        def sse_worker():
            try:
                logger.info(f"Starting SSE connection to {self.sse_url}")
                response = requests.get(self.sse_url, stream=True)
                
                # Log the response headers
                logger.info(f"Response headers: {dict(response.headers)}")
                
                # Log the raw content for the first few chunks
                chunk_count = 0
                raw_content = b""
                for chunk in response.iter_content(chunk_size=1024, decode_unicode=False):
                    raw_content += chunk
                    chunk_count += 1
                    if chunk_count <= 5:  # Log just the first 5 chunks
                        logger.info(f"Response chunk {chunk_count}: {chunk}")
                    if chunk_count >= 5:
                        break  # Just get enough for debugging
                
                # Log the decoded content
                try:
                    decoded_content = raw_content.decode('utf-8')
                    logger.info(f"Decoded content (first 1000 chars): {decoded_content[:1000]}")
                except UnicodeDecodeError as e:
                    logger.error(f"Failed to decode content: {e}")
                    logger.info(f"Raw content (hex): {raw_content.hex()[:200]}")
                
                # Now try to parse with SSEClient
                logger.info("Attempting to parse with SSEClient...")
                try:
                    # Get a fresh response for the SSEClient
                    response = requests.get(self.sse_url, stream=True)
                    client = sseclient.SSEClient(response)
                    for event in client.events():
                        if not self.running:
                            break
                            
                        logger.info(f"Received event: {event.event}, data: {event.data[:100]}...")
                        
                        if event.event == 'message':
                            try:
                                data = json.loads(event.data)
                                # Put the event in the thread-safe queue
                                self.event_queue.put(data)
                                logger.info(f"Added event to queue: {data.get('type', 'unknown')}")
                            except json.JSONDecodeError:
                                logger.error(f"Failed to decode SSE event data: {event.data}")
                            except Exception as e:
                                logger.error(f"Error processing SSE event: {str(e)}")
                except Exception as e:
                    logger.error(f"SSEClient parsing error: {e}")
                    
                    # Fall back to custom parsing
                    logger.info("Falling back to custom SSE parsing...")
                    response = requests.get(self.sse_url, stream=True)
                    
                    # Custom SSE parser
                    buffer = ""
                    event_data = ""
                    event_type = "message"  # Default event type
                    
                    for line in response.iter_lines(decode_unicode=True):
                        if not self.running:
                            break
                            
                        logger.debug(f"Raw line: {line}")
                        
                        if not line:
                            # Empty line means end of event
                            if event_data:
                                try:
                                    data = json.loads(event_data)
                                    logger.info(f"Parsed event: {event_type}, data: {data}")
                                    self.event_queue.put(data)
                                except json.JSONDecodeError as e:
                                    logger.error(f"Failed to decode event data: {event_data}, error: {e}")
                                
                                # Reset for next event
                                event_data = ""
                                event_type = "message"
                            continue
                        
                        # Parse the line
                        if line.startswith('data:'):
                            event_data += line[5:].strip()
                        elif line.startswith('event:'):
                            event_type = line[6:].strip()
                        elif line.startswith('id:'):
                            # Handle event ID if needed
                            pass
                        elif line.startswith('retry:'):
                            # Handle retry if needed
                            pass
                        # The Coral server might just be sending JSON directly
                        elif line.startswith('{'):
                            try:
                                data = json.loads(line)
                                logger.info(f"Parsed JSON event: {data}")
                                self.event_queue.put(data)
                            except json.JSONDecodeError:
                                logger.warning(f"Line starts with '{{' but is not valid JSON: {line}")
                        else:
                            logger.warning(f"Unknown SSE line format: {line}")
                    
            except Exception as e:
                logger.error(f"Error in SSE connection: {str(e)}")
        
        # Start the SSE thread
        self.sse_thread = threading.Thread(target=sse_worker, daemon=True)
        self.sse_thread.start()
        
        # Process events from the queue in the async context
        asyncio.create_task(self._process_events())
    
    async def _process_events(self):
        """Process events from the thread-safe queue."""
        while self.running:
            try:
                # Use a non-blocking get with a timeout to allow for clean shutdown
                try:
                    data = self.event_queue.get(block=False)
                except queue.Empty:
                    # No events in queue, sleep a bit and try again
                    await asyncio.sleep(0.1)
                    continue
                
                logger.info(f"Processing SSE event: {data.get('type', 'unknown')}")
                
                # Extract transport_session_id if present
                if 'transport_session_id' in data:
                    self.transport_session_id = data['transport_session_id']
                    logger.info(f"Received transport_session_id: {self.transport_session_id}")
                    self.connected = True
                    
                    # Process any pending operations
                    pending_ops = self.pending_operations.copy()
                    self.pending_operations = []
                    for operation in pending_ops:
                        await operation()
                
                await self._handle_message(data)
                self.event_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing event from queue: {str(e)}")
                # Sleep a bit to avoid tight loop in case of persistent errors
                await asyncio.sleep(0.1)

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
