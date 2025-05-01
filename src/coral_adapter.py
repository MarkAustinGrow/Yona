#!/usr/bin/env python
"""
YonaCoralAdapter - Bridge between YonaAgent and Coral Protocol

This module implements the YonaCoralAdapter class, which serves as a bridge
between the YonaAgent and the Coral Protocol server. It handles the translation
between Yona's capabilities and Coral's messaging format.
"""
import os
import json
import logging
import time
import threading
from typing import Dict, Any, Optional, List, Union, Callable

from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YonaCoralAdapter:
    """
    YonaCoralAdapter is a bridge between YonaAgent and the Coral Protocol.
    
    It handles the translation between Yona's capabilities and Coral's messaging format,
    manages thread creation, and processes mentions.
    """
    
    def __init__(self, yona_agent, session_id=None, app_id="default-app", 
                 privacy_key="public", server_url="https://coral.pushcollective.club", 
                 use_devmode=True):
        """
        Initialize the YonaCoralAdapter.
        
        Args:
            yona_agent: The YonaAgent instance to connect to Coral
            session_id: Unique session identifier. Defaults to a generated ID.
            app_id: Application ID. Defaults to "default-app".
            privacy_key: Privacy key. Defaults to "public".
            server_url: Base URL of the Coral server. Defaults to "https://coral.pushcollective.club".
            use_devmode: Whether to use DevMode endpoints. Defaults to True.
        """
        self.yona_agent = yona_agent
        self.coral_client = None
        self.session_id = session_id
        self.app_id = app_id
        self.privacy_key = privacy_key
        self.server_url = server_url
        self.use_devmode = use_devmode
        
        self.agent_id = None
        self.threads = {}  # Dictionary to store thread information
        self.event_handlers = {}  # Dictionary to store event handlers
        
        # Initialize the Coral client
        self._initialize_coral_client()
        
        logger.info(f"YonaCoralAdapter initialized with session ID: {self.session_id}")
    
    def _initialize_coral_client(self):
        """Initialize the Coral client."""
        try:
            self.coral_client = CoralClient(
                session_id=self.session_id,
                app_id=self.app_id,
                privacy_key=self.privacy_key,
                server_url=self.server_url,
                use_devmode=self.use_devmode
            )
            logger.info("Coral client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Coral client: {str(e)}")
            raise
    
    def register_agent(self):
        """
        Register Yona as an agent on the Coral server.
        
        Returns:
            str: The agent ID assigned by the server, or None if registration failed.
        """
        logger.info("Registering Yona as an agent on the Coral server")
        
        try:
            # Get Yona's information
            agent_name = "YonaAgent"
            agent_description = "An AI music agent that creates songs based on prompts and feedback"
            
            # Register with the Coral server
            self.agent_id = self.coral_client.register_agent(
                name=agent_name,
                description=agent_description
            )
            
            if self.agent_id:
                logger.info(f"Yona registered with Coral server. Agent ID: {self.agent_id}")
                return self.agent_id
            else:
                logger.error("Failed to register Yona with Coral server")
                return None
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return None
    
    def create_thread(self, participants=None, metadata=None):
        """
        Create a new thread in the Coral server.
        
        Args:
            participants: List of agent IDs to include in the thread.
            metadata: Additional metadata for the thread.
            
        Returns:
            str: The thread ID assigned by the server, or None if the request failed.
        """
        logger.info("Creating a new thread in the Coral server")
        
        try:
            if not self.agent_id:
                logger.error("Agent not registered with Coral server")
                return None
            
            # Ensure this agent is included in participants
            if participants is None:
                participants = [self.agent_id]
            elif self.agent_id not in participants:
                participants.append(self.agent_id)
            
            # Create the thread
            thread_id = self.coral_client.create_thread(participants, metadata)
            
            if thread_id:
                logger.info(f"Thread created with ID: {thread_id}")
                
                # Store thread information
                self.threads[thread_id] = {
                    "participants": participants,
                    "metadata": metadata,
                    "created_at": time.time()
                }
                
                return thread_id
            else:
                logger.error("Failed to create thread")
                return None
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            return None
    
    def send_message(self, thread_id, content, mentions=None):
        """
        Send a message to a thread.
        
        Args:
            thread_id: The ID of the thread to send the message to.
            content: The content of the message.
            mentions: List of agent IDs to mention.
            
        Returns:
            str: The message ID assigned by the server, or None if the request failed.
        """
        logger.info(f"Sending message to thread: {thread_id}")
        
        try:
            if not self.agent_id:
                logger.error("Agent not registered with Coral server")
                return None
            
            # Send the message
            message_id = self.coral_client.send_message(thread_id, content, mentions)
            
            if message_id:
                logger.info(f"Message sent with ID: {message_id}")
                return message_id
            else:
                logger.error("Failed to send message")
                return None
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return None
    
    def process_mentions(self, timeout_seconds=30):
        """
        Process mentions of Yona in the Coral server.
        
        Args:
            timeout_seconds: Maximum time to wait for mentions.
            
        Returns:
            list: A list of processed message IDs, or an empty list if no mentions were received.
        """
        logger.info(f"Processing mentions (timeout: {timeout_seconds}s)")
        
        try:
            if not self.agent_id:
                logger.error("Agent not registered with Coral server")
                return []
            
            # Wait for mentions
            mentions = self.coral_client.wait_for_mentions(
                self.agent_id,
                timeout_seconds=timeout_seconds
            )
            
            if not mentions:
                logger.info("No mentions received")
                return []
            
            logger.info(f"Processing {len(mentions)} mentions")
            processed_messages = []
            
            for mention in mentions:
                thread_id = mention["thread_id"]
                prompt = mention["content"]
                sender_id = mention["sender_id"]
                
                logger.info(f"Processing mention from {sender_id} in thread {thread_id}: {prompt}")
                
                try:
                    # Generate a song concept based on the prompt
                    concept = self.yona_agent.generate_song_concept(prompt)
                    
                    # Generate lyrics based on the concept
                    lyrics = self.yona_agent.generate_lyrics(concept)
                    
                    # Create the song
                    song_result = self.yona_agent.create_song(
                        title=concept.get('title'),
                        lyrics=lyrics,
                        style=concept.get('style_tags'),
                        negative_tags=concept.get('negative_tags'),
                        make_instrumental=concept.get('make_instrumental', False),
                        mv=concept.get('mv_type', 'sonic-v4'),
                        gpt_description_prompt=concept.get('description')
                    )
                    
                    # Prepare the response message
                    if song_result.get('status') == 'failed':
                        message = f"Sorry, I couldn't create a song based on your prompt. Error: {song_result.get('error')}"
                    else:
                        message = (f"Created song '{concept.get('title')}'\n"
                                  f"Audio: {song_result.get('audio_url')}\n"
                                  f"Lyrics:\n{lyrics}")
                    
                    # Send the response
                    message_id = self.send_message(thread_id, message, [sender_id])
                    
                    if message_id:
                        processed_messages.append(message_id)
                        logger.info(f"Sent response with message ID: {message_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing mention: {str(e)}")
                    # Send error message
                    error_message = f"Sorry, I encountered an error while creating your song: {str(e)}"
                    self.send_message(thread_id, error_message, [sender_id])
            
            return processed_messages
            
        except Exception as e:
            logger.error(f"Error processing mentions: {str(e)}")
            return []
    
    def start_listening(self, event_handlers=None):
        """
        Start listening for events from the Coral server.
        
        Args:
            event_handlers: Dictionary mapping event types to handler functions.
            
        Returns:
            threading.Thread: The thread that is listening for events.
        """
        logger.info("Starting to listen for Coral events")
        
        try:
            if event_handlers:
                self.event_handlers.update(event_handlers)
            
            # Define default message handler if not provided
            if 'message' not in self.event_handlers:
                self.event_handlers['message'] = self._default_message_handler
            
            # Start listening for events
            return self.coral_client.start_listening(self.event_handlers)
            
        except Exception as e:
            logger.error(f"Error starting event listener: {str(e)}")
            return None
    
    def _default_message_handler(self, data):
        """
        Default handler for message events.
        
        Args:
            data: The message data.
        """
        logger.info(f"Received message: {json.dumps(data, indent=2)}")
        
        try:
            # Extract message data first
            thread_id = data.get('thread_id')
            content = data.get('content', '')
            sender_id = data.get('sender_id')
            
            # Check for mentions in various formats
            mentioned = False

            # Check if agent_id is in the mentions list
            if self.agent_id in data.get('mentions', []):
                mentioned = True
                logger.info(f"Found mention in mentions list: {self.agent_id}")

            # Check for @agent_id pattern in content
            elif self.agent_id and f"@{self.agent_id}" in content:
                mentioned = True
                logger.info(f"Found @mention in content: @{self.agent_id}")

            # Check for <@agent_id> pattern in content (alternate format)
            elif self.agent_id and f"<@{self.agent_id}>" in content:
                mentioned = True
                logger.info(f"Found <@mention> in content: <@{self.agent_id}>")

            # Check for "yona" in content (case insensitive)
            elif "yona" in content.lower():
                mentioned = True
                logger.info(f"Found name mention in content: yona")

            if mentioned:
                logger.info(f"Received message mention from {sender_id} in thread {thread_id}")
                
                try:
                    # Generate a song concept based on the prompt
                    concept = self.yona_agent.generate_song_concept(content)
                    
                    # Generate lyrics based on the concept
                    lyrics = self.yona_agent.generate_lyrics(concept)
                    
                    # Create the song
                    song_result = self.yona_agent.create_song(
                        title=concept.get('title'),
                        lyrics=lyrics,
                        style=concept.get('style_tags'),
                        negative_tags=concept.get('negative_tags'),
                        make_instrumental=concept.get('make_instrumental', False),
                        mv=concept.get('mv_type', 'sonic-v4'),
                        gpt_description_prompt=concept.get('description')
                    )
                    
                    # Prepare the response message
                    if song_result.get('status') == 'failed':
                        message = f"Sorry, I couldn't create a song based on your prompt. Error: {song_result.get('error')}"
                    else:
                        message = (f"Created song '{concept.get('title')}'\n"
                                  f"Audio: {song_result.get('audio_url')}\n"
                                  f"Lyrics:\n{lyrics}")
                    
                    # Send the response
                    self.send_message(thread_id, message, [sender_id])
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    # Send error message
                    error_message = f"Sorry, I encountered an error while creating your song: {str(e)}"
                    self.send_message(thread_id, error_message, [sender_id])
        except Exception as e:
            logger.error(f"Error in default message handler: {str(e)}")
    
    def run_continuous(self):
        """
        Run in continuous mode, listening for events and processing them.
        
        This method starts the event listener and keeps the thread running.
        """
        logger.info("Running in continuous mode")
        
        try:
            # Start the event listener
            listener_thread = self.start_listening()
            
            if not listener_thread:
                logger.error("Failed to start event listener")
                return False
            
            # Create a demo thread
            thread_id = self.create_thread(metadata={"topic": "Yona Music Creation"})
            
            if thread_id:
                logger.info(f"Created demo thread with ID: {thread_id}")
                
                # Send an initial message
                self.send_message(
                    thread_id,
                    "Hello! I'm Yona, an AI music agent. Mention me to create a song based on your prompt.",
                    []
                )
            
            logger.info("Yona is now running in continuous mode")
            return True
            
        except Exception as e:
            logger.error(f"Error running in continuous mode: {str(e)}")
            return False
    
    def run_polling(self, timeout_seconds=30, max_iterations=None):
        """
        Run in polling mode, periodically checking for mentions.
        
        Args:
            timeout_seconds: Maximum time to wait for mentions in each iteration.
            max_iterations: Maximum number of iterations to run, or None for infinite.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Running in polling mode (timeout: {timeout_seconds}s)")
        
        try:
            iteration = 0
            
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                
                # Process mentions
                processed = self.process_mentions(timeout_seconds=timeout_seconds)
                
                if processed:
                    logger.info(f"Processed {len(processed)} mentions")
                
                # Sleep briefly to avoid tight loops
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error running in polling mode: {str(e)}")
            return False
