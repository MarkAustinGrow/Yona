#!/usr/bin/env python
"""
Coral Protocol LangChain Integration for Yona

This module provides integration between Yona and the Coral Protocol
using LangChain's MCP module.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Union

from src.coral_protocol.langchain import CoralRunnable, CoralRunnableConfig
from langchain.schema.runnable import Runnable
from langchain_openai import ChatOpenAI

from src.identity.did_manager import DIDManager
from src.protocol.capability_document import CapabilityDocument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YonaCoralAdapter:
    """
    Adapter for integrating Yona with the Coral Protocol using LangChain.
    
    This class provides functionality for:
    - Registering Yona's capabilities with a Coral server
    - Handling requests from other agents through the Coral Protocol
    - Sending requests to other agents through the Coral Protocol
    """
    
    def __init__(self, 
                 yona_agent,
                 coral_server_url: str,
                 openai_api_key: Optional[str] = None,
                 did_domain: str = "yona.ai",
                 private_key_path: Optional[str] = None):
        """
        Initialize the Yona Coral Adapter.
        
        Args:
            yona_agent: Instance of YonaAgent
            coral_server_url: URL of the Coral server
            openai_api_key: API key for OpenAI (optional, will use YonaAgent's key if not provided)
            did_domain: Domain for the did:web identifier
            private_key_path: Path to a file containing a private key for DID
        """
        self.yona_agent = yona_agent
        self.coral_server_url = coral_server_url
        self.openai_api_key = openai_api_key or yona_agent.openai_api_key
        
        # Use the DID manager from the Yona agent
        self.did_manager = yona_agent.did_manager
        self.capability_generator = yona_agent.capability_generator
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(api_key=self.openai_api_key)
        
        # Create Coral runnable configuration
        self.coral_config = CoralRunnableConfig(
            server_url=coral_server_url,
            did=self.did_manager.did,
            private_key=self._get_private_key_bytes(),
            capability_document=self.capability_generator.generate()
        )
        
        # Create Coral runnable
        self.coral_runnable = self._create_coral_runnable()
        
        logger.info(f"YonaCoralAdapter initialized with DID: {self.did_manager.did}")
        logger.info(f"Connected to Coral server at: {coral_server_url}")
    
    def _get_private_key_bytes(self) -> bytes:
        """
        Get the private key as bytes.
        
        Returns:
            Private key as bytes
        """
        from cryptography.hazmat.primitives import serialization
        
        private_key_bytes = self.did_manager.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return private_key_bytes
    
    def _create_coral_runnable(self) -> CoralRunnable:
        """
        Create a Coral runnable with Yona's capabilities.
        
        Returns:
            CoralRunnable instance
        """
        # Define the song creation function
        def create_song(prompt: str, **kwargs) -> Dict[str, Any]:
            """Create a song based on a prompt."""
            logger.info(f"Creating song from prompt: {prompt}")
            
            # Generate song concept
            concept = self.yona_agent.generate_song_concept(prompt)
            
            # Generate lyrics
            lyrics = self.yona_agent.generate_lyrics(concept)
            
            # Create the song
            song = self.yona_agent.create_song(
                title=concept.get('title'),
                lyrics=lyrics,
                style=concept.get('style_tags'),
                negative_tags=concept.get('negative_tags'),
                make_instrumental=concept.get('make_instrumental', False),
                mv=concept.get('mv_type', 'sonic-v4'),
                gpt_description_prompt=concept.get('description', ''),
                **kwargs
            )
            
            return song
        
        # Define the feedback processing function
        def process_feedback(song_id: str, feedback_text: str, rating: Optional[int] = None) -> Dict[str, Any]:
            """Process feedback for a song."""
            logger.info(f"Processing feedback for song {song_id}")
            
            # Get the original song
            original_song = self.yona_agent.supabase_client.get_song_by_id(song_id)
            if not original_song:
                logger.error(f"Original song {song_id} not found")
                return {"status": "failed", "error": f"Original song {song_id} not found"}
            
            # Create a feedback record
            feedback_id = self.yona_agent.supabase_client.store_feedback({
                'song_id': song_id,
                'comments': feedback_text,
                'rating': rating or 3  # Default to 3 if not provided
            })
            
            if not feedback_id:
                logger.error("Failed to store feedback")
                return {"status": "failed", "error": "Failed to store feedback"}
            
            # Extract parameters from the original song
            original_params = original_song.get('params_used', {})
            if not original_params:
                logger.warning(f"No params_used found for song {song_id}, using defaults")
                original_params = {
                    'prompt': original_song.get('lyrics', ''),
                    'title': original_song.get('title', 'Untitled'),
                    'style': original_song.get('style', ''),
                    'negative_tags': original_song.get('negative_tags', ''),
                    'make_instrumental': original_song.get('make_instrumental', False),
                    'mv': original_song.get('mv', 'sonic-v4'),
                    'gpt_description_prompt': original_song.get('gpt_description', ''),
                    'voice_gender': 'female'
                }
            
            # Use OpenAI to modify parameters based on feedback
            system_message = """
            You are an AI assistant that helps modify song generation parameters based on user feedback.
            Analyze the feedback and suggest modifications to the original parameters.
            Return a JSON object with the modified parameters.
            """
            
            user_message = f"""
            Original parameters:
            {json.dumps(original_params, indent=2)}
            
            User feedback:
            {feedback_text}
            
            Please modify the parameters based on the feedback. Return only the JSON object with the modified parameters.
            """
            
            response = self.yona_agent.openai_client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Parse the response
            modified_params_text = response.choices[0].message.content
            modified_params = json.loads(modified_params_text)
            
            # Create a new song with the modified parameters
            api_to_use = original_params.get('api_used', 'sonic')
            
            if api_to_use == 'nuro':
                # Create song with Nuro API
                new_song = self.yona_agent.create_song(
                    title=modified_params.get('title'),
                    lyrics=modified_params.get('prompt'),  # For Nuro, prompt contains lyrics
                    api='nuro',
                    gender=modified_params.get('gender', 'Female'),
                    genre=modified_params.get('genre', 'Pop'),
                    mood=modified_params.get('mood', 'Happy'),
                    timbre=modified_params.get('timbre', 'Powerful'),
                    duration=modified_params.get('duration', 60),
                    mv=modified_params.get('mv', 'sonic-v4')
                )
            else:
                # Create song with Sonic API
                new_song = self.yona_agent.create_song(
                    title=modified_params.get('title'),
                    lyrics=modified_params.get('prompt'),
                    style=modified_params.get('style'),
                    negative_tags=modified_params.get('negative_tags'),
                    make_instrumental=modified_params.get('make_instrumental', False),
                    mv=modified_params.get('mv', 'sonic-v4'),
                    gpt_description_prompt=modified_params.get('gpt_description_prompt'),
                    voice_gender=modified_params.get('voice_gender', 'female')
                )
            
            # If successful, update the feedback record
            if new_song.get('status') != 'failed':
                # Add references to original song and feedback
                new_song['original_song_id'] = song_id
                new_song['feedback_id'] = feedback_id
                
                # Update the feedback record
                self.yona_agent.supabase_client.update_feedback(feedback_id, {
                    'rating': rating or 5,  # Mark as processed with a default rating
                    'processed_at': 'now()',
                    'new_song_id': new_song.get('id')
                })
                
                # Store as a version in the song_versions table
                version_data = {
                    'song_id': song_id,
                    'title': new_song.get('title'),
                    'lyrics': new_song.get('lyrics'),
                    'audio_url': new_song.get('audio_url'),
                    'params_used': modified_params
                }
                self.yona_agent.supabase_client.store_song_version(song_id, version_data)
            
            return new_song
        
        # Define the song listing function
        def list_songs(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
            """List songs from the database."""
            logger.info(f"Listing songs (limit: {limit}, offset: {offset})")
            
            # Get songs from Supabase
            songs = self.yona_agent.supabase_client.list_songs(limit=limit, offset=offset)
            return songs
        
        # Create a dictionary of functions to expose through Coral
        functions = {
            "create_song": create_song,
            "process_feedback": process_feedback,
            "list_songs": list_songs
        }
        
        # Create the Coral runnable
        coral_runnable = CoralRunnable(
            functions=functions,
            config=self.coral_config
        )
        
        return coral_runnable
    
    def register_with_coral_server(self) -> bool:
        """
        Register Yona's capabilities with the Coral server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # The registration happens automatically when the CoralRunnable is created
            # We just need to make sure it's initialized
            if self.coral_runnable:
                logger.info(f"Successfully registered with Coral server at {self.coral_server_url}")
                return True
            else:
                logger.error("Coral runnable not initialized")
                return False
        except Exception as e:
            logger.error(f"Error registering with Coral server: {str(e)}")
            return False
    
    def call_agent(self, agent_did: str, function_name: str, **kwargs) -> Any:
        """
        Call a function on another agent through the Coral Protocol.
        
        Args:
            agent_did: DID of the agent to call
            function_name: Name of the function to call
            **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        try:
            logger.info(f"Calling {function_name} on agent {agent_did}")
            
            # Create the function call
            result = self.coral_runnable.call_agent(
                agent_did=agent_did,
                function_name=function_name,
                **kwargs
            )
            
            logger.info(f"Successfully called {function_name} on agent {agent_did}")
            return result
        except Exception as e:
            logger.error(f"Error calling agent {agent_did}: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """
        Discover agents registered with the Coral server.
        
        Returns:
            List of dictionaries containing agent information
        """
        try:
            logger.info(f"Discovering agents on Coral server {self.coral_server_url}")
            
            # Get the list of agents
            agents = self.coral_runnable.discover_agents()
            
            logger.info(f"Discovered {len(agents)} agents")
            return agents
        except Exception as e:
            logger.error(f"Error discovering agents: {str(e)}")
            return []
    
    def get_agent_capabilities(self, agent_did: str) -> Dict[str, Any]:
        """
        Get the capabilities of an agent.
        
        Args:
            agent_did: DID of the agent
            
        Returns:
            Dictionary containing the agent's capabilities
        """
        try:
            logger.info(f"Getting capabilities for agent {agent_did}")
            
            # Get the agent's capabilities
            capabilities = self.coral_runnable.get_agent_capabilities(agent_did)
            
            logger.info(f"Successfully retrieved capabilities for agent {agent_did}")
            return capabilities
        except Exception as e:
            logger.error(f"Error getting capabilities for agent {agent_did}: {str(e)}")
            return {}
    
    def start_server(self, host: str = '0.0.0.0', port: int = 5001) -> None:
        """
        Start a server to listen for requests from the Coral Protocol.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        try:
            logger.info(f"Starting Coral server on {host}:{port}")
            
            # Start the server
            self.coral_runnable.start_server(host=host, port=port)
            
            logger.info(f"Coral server started on {host}:{port}")
        except Exception as e:
            logger.error(f"Error starting Coral server: {str(e)}")
            raise
