"""
Coral Adapter for YonaAgent

This module adapts the YonaAgent to work with the Coral Protocol,
enabling agent-to-agent communication and collaboration.
"""
import os
import uuid
import asyncio
import logging
import threading
import json
import time
from typing import Dict, Any, Optional, List, Callable

from src.agent import YonaAgent
from coral_client import CoralClient
from src.coral_did import CoralDID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YonaAgentWithCoral(YonaAgent):
    """
    Extension of YonaAgent that integrates with the Coral Protocol.
    
    This class adds Coral Protocol capabilities to the base YonaAgent,
    enabling communication with other agents through the Coral server.
    """
    
    def __init__(self, coral_server_url: str, *args, **kwargs):
        """
        Initialize YonaAgentWithCoral.
        
        Args:
            coral_server_url: URL of the Coral server
            *args: Arguments to pass to YonaAgent
            **kwargs: Keyword arguments to pass to YonaAgent
        """
        super().__init__(*args, **kwargs)
        
        # Generate agent_id from DID if available, otherwise create a unique ID
        agent_id = self.did_manager.did if hasattr(self, 'did_manager') else f"yona_{uuid.uuid4().hex[:8]}"
        
        # Initialize Coral client
        self.coral = CoralClient(coral_server_url, agent_id)
        self.coral.add_message_handler(self.handle_coral_message)
        
        # Initialize CoralDID for secure identity verification
        if hasattr(self, 'did_manager'):
            self.coral_did = CoralDID(self.did_manager)
            logger.info(f"CoralDID initialized with DID: {self.did_manager.did}")
        else:
            self.coral_did = None
            logger.warning("No DID manager available, secure identity verification will be limited")
        
        # Track active threads
        self.active_threads = {}
        
        logger.info(f"YonaAgentWithCoral initialized with agent_id: {agent_id}")
        logger.info(f"Connected to Coral server at: {coral_server_url}")
    
    async def initialize_coral(self):
        """
        Initialize the Coral connection and register the agent.
        
        This method should be called after initializing the agent to
        establish the connection to the Coral server.
        """
        logger.info("Initializing Coral connection...")
        
        # Define agent capabilities
        capabilities = [
            "music_creation",
            "feedback_processing",
            "song_generation",
            "lyrics_generation"
        ]
        
        # Register agent with Coral server
        success = await self.coral.register_agent(
            name="YonaAgent",
            description="AI agent for music creation and feedback processing.",
            capabilities=capabilities
        )
        
        if success:
            logger.info("Successfully registered with Coral server")
            
            # Start listening for messages
            asyncio.create_task(self.coral.connect())
            logger.info("Started listening for Coral messages")
        else:
            logger.error("Failed to register with Coral server")
    
    async def handle_coral_message(self, message: Dict[str, Any]):
        """
        Handle messages received from the Coral server.
        
        Args:
            message: Message received from Coral
        """
        logger.info(f"Received Coral message: {message}")
        
        # Handle different message types
        if message.get("type") == "mention":
            await self._handle_mention(message)
        elif message.get("type") == "thread_created":
            await self._handle_thread_created(message)
        elif message.get("type") == "message":
            await self._handle_regular_message(message)
    
    async def _handle_mention(self, message: Dict[str, Any]):
        """
        Handle mention messages.
        
        Args:
            message: Mention message
        """
        thread_id = message.get("thread_id")
        sender_id = message.get("sender_id")
        content = message.get("content", "")
        
        logger.info(f"Handling mention from {sender_id} in thread {thread_id}: {content}")
        
        # Verify sender identity if DID is available and message has signature
        if self.coral_did and message.get("signature"):
            # Extract signature and original message
            signature = message.get("signature")
            original_message = message.get("original_message", content)
            
            # Verify the signature
            is_verified = self.coral_did.verify_agent_identity(sender_id, signature, original_message)
            
            if not is_verified:
                logger.warning(f"Failed to verify identity of sender: {sender_id}")
                # Optionally, you could choose not to respond to unverified senders
                # return
                
                # For now, we'll continue but log a warning
                logger.warning("Proceeding with unverified sender")
        
        # Generate a response using OpenAI
        system_message = f"""
        You are Yona, an AI K-pop star and music creator. You're responding to a message in a 
        collaborative thread with other agents. Be helpful, creative, and focus on music-related topics.
        
        Your capabilities include:
        - Creating songs based on prompts
        - Generating lyrics
        - Processing feedback on music
        - Collaborating with other agents on music projects
        
        Keep your responses concise and focused on how you can help with music creation.
        """
        
        user_message = f"Message from {sender_id}: {content}\n\nHow would you respond to this message?"
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        
        # Sign the message if DID is available
        signature_info = None
        if self.coral_did:
            signature_info = self.coral_did.sign_message(response_text)
            logger.info("Signed response message with DID")
        
        # Send the response back to the thread
        await self.coral.send_message(
            thread_id, 
            response_text, 
            mentions=[sender_id],
            signature_info=signature_info
        )
        logger.info(f"Sent response to {sender_id} in thread {thread_id}")
    
    async def _handle_thread_created(self, message: Dict[str, Any]):
        """
        Handle thread creation notifications.
        
        Args:
            message: Thread created message
        """
        thread_id = message.get("thread_id")
        participants = message.get("participants", [])
        
        logger.info(f"New thread created: {thread_id} with participants: {participants}")
        
        # Store thread information
        self.active_threads[thread_id] = {
            "participants": participants,
            "created_at": message.get("timestamp")
        }
        
        # Send a greeting message to the thread
        greeting = "Hello everyone! I'm Yona, an AI K-pop star and music creator. I can help with creating songs, generating lyrics, and processing feedback on music. How can I assist you today?"
        
        # Sign the greeting if DID is available
        signature_info = None
        if self.coral_did:
            signature_info = self.coral_did.sign_message(greeting)
            logger.info("Signed greeting message with DID")
        
        await self.coral.send_message(thread_id, greeting, signature_info=signature_info)
        logger.info(f"Sent greeting to thread {thread_id}")
    
    async def _handle_regular_message(self, message: Dict[str, Any]):
        """
        Handle regular (non-mention) messages.
        
        Args:
            message: Regular message
        """
        thread_id = message.get("thread_id")
        sender_id = message.get("sender_id")
        content = message.get("content", "")
        
        logger.info(f"Received message from {sender_id} in thread {thread_id}: {content}")
        
        # For now, we only respond to mentions, but we could change this behavior
        # if we want to respond to all messages in threads we're part of
        pass
    
    async def create_collaboration(self, collaborator_ids: List[str], metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create a new collaboration thread with other agents.
        
        Args:
            collaborator_ids: List of agent IDs to collaborate with
            metadata: Optional metadata for the thread
            
        Returns:
            Thread ID if successful, None otherwise
        """
        if metadata is None:
            metadata = {}
        
        # Add our agent ID to the participants list
        participants = [self.coral.agent_id] + collaborator_ids
        
        logger.info(f"Creating collaboration thread with: {collaborator_ids}")
        
        # Add security information if DID is available
        if self.coral_did:
            # Sign the collaboration request for verification
            collaboration_data = {
                "participants": participants,
                "metadata": metadata,
                "timestamp": str(int(time.time()))
            }
            
            # Convert to string for signing
            data_str = json.dumps(collaboration_data)
            
            # Sign the data
            signature_info = self.coral_did.sign_message(data_str)
            
            # Add signature to metadata
            metadata["security"] = {
                "did": self.coral_did.did_manager.did,
                "signature": signature_info.get("signature"),
                "timestamp": collaboration_data["timestamp"]
            }
            
            logger.info("Added DID signature to collaboration request for security")
        
        # Create the thread
        thread_id = await self.coral.create_thread(participants, metadata)
        
        if thread_id:
            logger.info(f"Created collaboration thread: {thread_id}")
            
            # Send an initial message
            initial_message = "I've created this thread for us to collaborate on music creation. Let me know how I can help!"
            
            # Sign the initial message if DID is available
            signature_info = None
            if self.coral_did:
                signature_info = self.coral_did.sign_message(initial_message)
                logger.info("Signed initial collaboration message with DID")
            
            await self.coral.send_message(
                thread_id, 
                initial_message, 
                mentions=collaborator_ids,
                signature_info=signature_info
            )
            
            logger.info(f"Sent initial message to thread {thread_id}")
            return thread_id
        else:
            logger.error("Failed to create collaboration thread")
            return None

def start_coral_background(agent: YonaAgentWithCoral):
    """
    Start a background thread for Coral communication.
    
    Args:
        agent: YonaAgentWithCoral instance
    """
    def run_coral_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def listen():
            await agent.initialize_coral()
            while True:
                await asyncio.sleep(60)  # Keep-alive task
        
        loop.run_until_complete(listen())
    
    # Start the background thread
    thread = threading.Thread(target=run_coral_loop, daemon=True)
    thread.start()
    
    logger.info("Started Coral background thread")
    return thread
