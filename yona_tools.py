#!/usr/bin/env python
"""
Yona CrewAI Tools

This module defines the CrewAI tools that expose Yona's functionality.
"""
import logging
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from yona_implementation import YonaImplementationManager

logger = logging.getLogger(__name__)

# Initialize the Yona implementation manager
yona_manager = YonaImplementationManager()

class GenerateSongTool(BaseTool):
    """Tool to generate a song based on a prompt."""
    
    name: str = "generate_song"
    description: str = "Generate a song based on a prompt"
    
    def _run(self, prompt: str, api: str = "sonic", **kwargs) -> Dict[str, Any]:
        """
        Generate a song based on a prompt
        
        Args:
            prompt: The prompt describing the song to create
            api: Which API to use ('sonic' or 'nuro')
            **kwargs: Additional parameters for song creation
            
        Returns:
            Dictionary containing the song data, including URLs and metadata
        """
        return yona_manager.generate_song(prompt, api, **kwargs)

class ProcessFeedbackTool(BaseTool):
    """Tool to process feedback for a song."""
    
    name: str = "process_feedback"
    description: str = "Process feedback for a song to create an improved version"
    
    def _run(self, song_id: str, feedback_id: str) -> Dict[str, Any]:
        """
        Process feedback for a song
        
        Args:
            song_id: ID of the original song
            feedback_id: ID of the feedback to process
            
        Returns:
            Dictionary containing the new song data
        """
        return yona_manager.process_feedback(song_id, feedback_id)

class ListSongsTool(BaseTool):
    """Tool to list songs from the database."""
    
    name: str = "list_songs"
    description: str = "List songs from the database"
    
    def _run(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List songs from the database
        
        Args:
            limit: Maximum number of songs to return
            offset: Offset for pagination
            
        Returns:
            List of dictionaries containing song data
        """
        return yona_manager.list_songs(limit, offset)

class GetSongTool(BaseTool):
    """Tool to get a specific song by ID."""
    
    name: str = "get_song"
    description: str = "Get a specific song by ID"
    
    def _run(self, song_id: str) -> Dict[str, Any]:
        """
        Get a specific song by ID
        
        Args:
            song_id: ID of the song to retrieve
            
        Returns:
            Dictionary containing the song data
        """
        return yona_manager.get_song(song_id)

class GetCapabilityDocumentTool(BaseTool):
    """Tool to get the capability document for the agent."""
    
    name: str = "get_capability_document"
    description: str = "Get the capability document for the agent"
    
    def _run(self) -> Dict[str, Any]:
        """
        Get the capability document for the agent
        
        Returns:
            Dictionary containing the capability document
        """
        return yona_manager.get_capability_document()

class GetDIDDocumentTool(BaseTool):
    """Tool to get the DID document for the agent."""
    
    name: str = "get_did_document"
    description: str = "Get the DID document for the agent"
    
    def _run(self) -> Dict[str, Any]:
        """
        Get the DID document for the agent
        
        Returns:
            Dictionary containing the DID document
        """
        return yona_manager.get_did_document()

class ProcessUserRequestTool(BaseTool):
    """Tool to process a natural language request from the user."""
    
    name: str = "process_user_request"
    description: str = "Process a natural language request from the user"
    
    def _run(self, user_input: str) -> Dict[str, Any]:
        """
        Process a natural language request from the user
        
        Args:
            user_input: String containing the user's request
            
        Returns:
            Dictionary with results and response
        """
        return yona_manager.process_user_request(user_input)

def get_yona_tools() -> List[BaseTool]:
    """
    Get the list of CrewAI tools that expose Yona's functionality
    
    Returns:
        List of CrewAI Tool objects
    """
    logger.info("Creating Yona tools for CrewAI")
    
    tools = [
        GenerateSongTool(),
        ProcessFeedbackTool(),
        ListSongsTool(),
        GetSongTool(),
        GetCapabilityDocumentTool(),
        GetDIDDocumentTool(),
        ProcessUserRequestTool()
    ]
    
    logger.info(f"Created {len(tools)} tools for CrewAI")
    return tools
