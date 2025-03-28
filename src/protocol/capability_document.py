"""
Capability Document Generator for Yona MCP implementation.

This module provides functionality for generating capability documents
that describe the services and protocols supported by the Yona agent.
"""
import json
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CapabilityDocument:
    """
    Generator for capability documents that describe Yona's services.
    
    This class provides functionality for:
    - Creating capability documents in JSON-LD format
    - Describing Yona's music-related services
    - Specifying supported protocols and data formats
    """
    
    def __init__(self, did: str, agent_name: str = "Yona AI", 
                 agent_description: str = "An AI K-pop star that creates songs based on prompts and feedback"):
        """
        Initialize the Capability Document generator.
        
        Args:
            did: The DID of the agent
            agent_name: Name of the agent
            agent_description: Description of the agent
        """
        self.did = did
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.services = []
        self.protocols = {
            "supported": ["json", "jsonld"],
            "preferred": "json",
            "versions": ["v1"]
        }
        
        # Add default services
        self._add_default_services()
        
        logger.info(f"Capability Document generator initialized for {agent_name}")
    
    def _add_default_services(self) -> None:
        """Add default services for the Yona agent."""
        # Song creation service
        self.add_service(
            service_id="song-creation",
            service_type="MusicCreationService",
            description="Creates songs based on prompts",
            input_schema={
                "prompt": "string",
                "title": "string?",
                "style": "string?",
                "negative_tags": "string?",
                "make_instrumental": "boolean?",
                "mv": "string?",
                "voice_gender": "string?"
            },
            output_schema={
                "song_id": "string",
                "title": "string",
                "audio_url": "string",
                "video_url": "string?",
                "image_url": "string?"
            }
        )
        
        # Feedback processing service
        self.add_service(
            service_id="feedback-processing",
            service_type="FeedbackProcessingService",
            description="Creates new songs based on feedback for existing songs",
            input_schema={
                "song_id": "string",
                "feedback_text": "string",
                "rating": "number?"
            },
            output_schema={
                "new_song_id": "string",
                "title": "string",
                "audio_url": "string"
            }
        )
        
        # Song listing service
        self.add_service(
            service_id="song-listing",
            service_type="SongListingService",
            description="Lists songs created by the agent",
            input_schema={
                "limit": "number?",
                "offset": "number?"
            },
            output_schema={
                "songs": "array",
                "total_count": "number"
            }
        )
    
    def add_service(self, service_id: str, service_type: str, description: str,
                   input_schema: Dict[str, str], output_schema: Dict[str, str]) -> None:
        """
        Add a service to the capability document.
        
        Args:
            service_id: Unique identifier for the service
            service_type: Type of service
            description: Description of the service
            input_schema: Schema for service inputs
            output_schema: Schema for service outputs
        """
        service = {
            "id": f"{self.did}#{service_id}",
            "type": service_type,
            "description": description,
            "input": input_schema,
            "output": output_schema
        }
        
        self.services.append(service)
        logger.info(f"Added service: {service_id}")
    
    def update_protocols(self, supported: Optional[List[str]] = None, 
                        preferred: Optional[str] = None,
                        versions: Optional[List[str]] = None) -> None:
        """
        Update the supported protocols.
        
        Args:
            supported: List of supported protocol formats
            preferred: Preferred protocol format
            versions: List of supported protocol versions
        """
        if supported:
            self.protocols["supported"] = supported
        
        if preferred:
            self.protocols["preferred"] = preferred
        
        if versions:
            self.protocols["versions"] = versions
        
        logger.info(f"Updated protocols: {self.protocols}")
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate the capability document.
        
        Returns:
            The capability document as a dictionary
        """
        document = {
            "@context": "https://schema.org",
            "id": self.did,
            "name": self.agent_name,
            "description": self.agent_description,
            "services": self.services,
            "protocols": self.protocols
        }
        
        logger.info(f"Generated capability document for {self.agent_name}")
        return document
    
    def generate_json(self, pretty: bool = True) -> str:
        """
        Generate the capability document as a JSON string.
        
        Args:
            pretty: Whether to format the JSON with indentation
            
        Returns:
            The capability document as a JSON string
        """
        document = self.generate()
        
        if pretty:
            return json.dumps(document, indent=2)
        else:
            return json.dumps(document)
    
    def save_to_file(self, path: str) -> bool:
        """
        Save the capability document to a file.
        
        Args:
            path: Path to save the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(path, "w") as f:
                json.dump(self.generate(), f, indent=2)
            
            logger.info(f"Saved capability document to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving capability document: {str(e)}")
            return False


def generate_capability_document(did: str) -> Dict[str, Any]:
    """
    Generate a capability document for Yona.
    
    Args:
        did: The DID of the agent
        
    Returns:
        The capability document as a dictionary
    """
    generator = CapabilityDocument(did)
    return generator.generate()
