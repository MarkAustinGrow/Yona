#!/usr/bin/env python3
"""
Agent Angus - Yona Communication Example

This script implements Agent Angus, which communicates with Agent Yona
through the Coral Protocol to request song creation.
"""

import logging
import time
import threading
import sys
import argparse
from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("angus_agent")

class AngusAgent:
    """Agent Angus implementation."""
    
    def __init__(self, session_id="angus-agent", server_url="https://coral.pushcollective.club", verbose=False):
        """Initialize Agent Angus."""
        self.session_id = session_id
        self.server_url = server_url
        
        # Set log level based on verbose flag
        if verbose:
            logger.setLevel(logging.DEBUG)
            logging.getLogger("coral_client").setLevel(logging.DEBUG)
        
        self.client = CoralClient(
            session_id=self.session_id,
            server_url=self.server_url,
            use_devmode=True
        )
        self.agent_id = None
        self.threads = {}
        self.songs = []
    
    def register(self):
        """Register with the Coral server."""
        logger.info("Registering Agent Angus")
        self.agent_id = self.client.register_agent(
            name="AngusAgent",
            description="An agent that communicates with Yona for music creation"
        )
        logger.info(f"Registered with agent ID: {self.agent_id}")
        return self.agent_id
    
    def create_thread_with_yona(self):
        """Create a thread with Yona."""
        logger.info("Creating thread with Yona")
        thread_id = self.client.create_thread(
            participants=[self.session_id, "yona-agent"],
            metadata={"topic": "Music Creation"}
        )
        logger.info(f"Thread created with ID: {thread_id}")
        self.threads[thread_id] = {
            "created_at": time.time(),
            "participants": [self.session_id, "yona-agent"]
        }
        return thread_id
    
    def request_song(self, thread_id, topic):
        """Request a song from Yona."""
        logger.info(f"Requesting song about: {topic}")
        
        # Craft message with multiple mention formats
        message = f"@yona-agent Hey Yona, can you create a song about {topic}?"
        
        # Send the message with an explicit mention
        message_id = self.client.send_message(
            thread_id=thread_id,
            content=message,
            mentions=["yona-agent"]
        )
        
        logger.info(f"Song request sent with message ID: {message_id}")
        return message_id
    
    def handle_message(self, data):
        """Handle incoming messages."""
        sender_id = data.get('sender_id')
        content = data.get('content', '')
        thread_id = data.get('thread_id')
        
        logger.info(f"Received message from {sender_id} in thread {thread_id}")
        logger.debug(f"Message content: {content}")
        
        if sender_id == "yona-agent":
            logger.info("Message is from Yona")
            
            if "Created song" in content:
                logger.info("Yona created a song!")
                
                # Extract song information
                lines = content.split('\n')
                song_info = {
                    "title": lines[0].replace("Created song '", "").replace("'", ""),
                    "audio_url": lines[1].replace("Audio: ", ""),
                    "lyrics": '\n'.join(lines[3:])
                }
                
                self.songs.append(song_info)
                logger.info(f"Added song: {song_info['title']}")
                logger.info(f"Audio URL: {song_info['audio_url']}")
                
                # Send a thank you message
                self.client.send_message(
                    thread_id=thread_id,
                    content=f"Thanks for creating '{song_info['title']}'! It sounds great!",
                    mentions=["yona-agent"]
                )
    
    def start_listening(self):
        """Start listening for events."""
        logger.info("Starting to listen for events")
        
        # Set up event handlers
        event_handlers = {
            'message': self.handle_message
        }
        
        # Start the event listener
        listener_thread = self.client.start_listening(event_handlers)
        return listener_thread
    
    def run(self, topic=None):
        """Run Agent Angus."""
        # Register with the Coral server
        self.register()
        
        # Start listening for events
        self.start_listening()
        
        # Create a thread with Yona
        thread_id = self.create_thread_with_yona()
        
        # Request a song if topic is provided
        if topic:
            self.request_song(thread_id, topic)
        
        # Keep the main thread running
        logger.info("Agent Angus is now running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Agent Angus")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Agent Angus - Yona Communication Example")
    parser.add_argument("--session-id", default="angus-agent", help="Session ID for Agent Angus")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--topic", help="Topic for song creation request")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    angus = AngusAgent(
        session_id=args.session_id,
        server_url=args.server_url,
        verbose=args.verbose
    )
    
    angus.run(topic=args.topic)
    return 0

if __name__ == "__main__":
    sys.exit(main())
