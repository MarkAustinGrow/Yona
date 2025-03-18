"""
MusicAPI - Client for interacting with MusicAPI.ai service.
"""
import os
import json
import time
import logging
import httpx
from typing import Dict, Any, Optional, List, Union

from src.config.config import MUSICAPI_KEY, MUSICAPI_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicAPI:
    """
    Client for the MusicAPI.ai service that handles song and persona creation.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, simulation_mode: bool = False):
        """
        Initialize the MusicAPI client.
        
        Args:
            api_key: API key for MusicAPI.ai (defaults to environment variable)
            base_url: Base URL for the API (defaults to the standard MusicAPI URL)
            simulation_mode: If True, will simulate responses instead of calling the API
        """
        self.api_key = api_key or MUSICAPI_KEY
        self.base_url = base_url or MUSICAPI_BASE_URL
        self.simulation_mode = simulation_mode
        
        # Validate API key
        if not self.api_key and not simulation_mode:
            logger.warning("MusicAPI key is missing! Using simulation mode.")
            self.simulation_mode = True
        
        # Log initialization
        if self.simulation_mode:
            logger.info("MusicAPI initialized in simulation mode")
        else:
            logger.info(f"MusicAPI initialized with live API (key: {self.api_key[:5]}...)")
            logger.info("NOTE: Persona creation is currently unstable according to MusicAPI support")
            logger.info("Using direct song generation without persona")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.
        
        Returns:
            Dictionary with Content-Type and Authorization headers
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def create_song(
        self,
        prompt: str,
        title: Optional[str] = None,
        style: Optional[str] = None,
        negative_tags: Optional[str] = None,
        make_instrumental: bool = False,
        mv: str = 'sonic-v4',
        gpt_description_prompt: Optional[str] = None,
        voice_gender: str = 'female'
    ) -> Dict[str, Any]:
        """
        Create a song using MusicAPI.
        
        Args:
            prompt: Lyrics or prompt for the song
            title: Song title
            style: Style tags (comma separated)
            negative_tags: Tags to avoid in generation
            make_instrumental: Whether to make an instrumental version
            mv: Music video generation type
            gpt_description_prompt: Description prompt for the song
            voice_gender: Voice gender for the song (female or male)
            
        Returns:
            Dictionary with task_id, message, and status
        """
        if self.simulation_mode:
            logger.info("Simulation mode - returning mock response")
            return {
                'task_id': 'simulated-task-id',
                'message': 'Song creation task initiated successfully (simulated)',
                'status': 'pending'
            }
        
        # Log the prompt
        logger.info(f"Creating song with prompt: {prompt[:100]}...")
        
        # Prepare headers
        headers = self._get_headers()
        logger.info(f"Using API key: {self.api_key}")
        logger.info(f"Headers: {headers}")
        
        # Prepare payload
        payload = {
            'custom_mode': True,
            'prompt': prompt,
            'mv': mv,
            'make_instrumental': make_instrumental
        }
        
        # Add optional parameters if provided
        if title:
            payload['title'] = title
            
        # Add style tags and voice gender
        if style:
            # Check if voice_gender is already included in style
            if voice_gender and f"{voice_gender} voice" not in style.lower():
                payload['tags'] = f"{style}, {voice_gender} voice"
            else:
                payload['tags'] = style
        elif voice_gender:
            payload['tags'] = f"{voice_gender} voice"
            
        if negative_tags:
            payload['negative_tags'] = negative_tags
            
        if gpt_description_prompt:
            # Limit length to avoid 400 error
            if gpt_description_prompt and len(gpt_description_prompt) > 199:
                gpt_description_prompt = gpt_description_prompt[:199]
            payload['gpt_description_prompt'] = gpt_description_prompt
        
        # Log the payload
        logger.info(f"Payload: {payload}")
        
        # Make the API request
        url = f"{self.base_url}/api/v1/sonic/create"
        logger.info(f"Sending request to: {url}")
        
        try:
            response = httpx.post(url, json=payload, headers=headers)
            logger.info(f"Song creation response status: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                task_id = response_data.get('task_id')
                logger.info(f"Song creation task initiated with ID: {task_id}")
                
                return {
                    'task_id': task_id,
                    'message': 'Song creation task initiated successfully',
                    'status': 'pending'
                }
            else:
                logger.error(f"Error creating song: {response.text}")
                return {
                    'error': response.text,
                    'status': 'failed'
                }
                
        except Exception as e:
            logger.error(f"Exception creating song: {str(e)}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def check_song_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a song creation task.
        
        Args:
            task_id: Task ID from song creation
            
        Returns:
            Response JSON from the API
        """
        if self.simulation_mode:
            logger.info("Simulation mode - returning mock status")
            return {
                'data': [{
                    'state': 'succeeded',
                    'title': 'Simulated Song',
                    'audio_url': 'https://example.com/simulated-audio.mp3',
                    'video_url': 'https://example.com/simulated-video.mp4',
                    'image_url': 'https://example.com/simulated-image.jpg',
                    'duration': 180.0
                }],
                'message': 'success'
            }
        
        # Make the API request
        url = f"{self.base_url}/api/v1/sonic/task/{task_id}"
        logger.info(f"Checking status at: {url}")
        
        try:
            response = httpx.get(url, headers=self._get_headers())
            logger.info(f"Song status check response: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error checking song status: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception checking song status: {str(e)}")
            return None
    
    def create_persona(
        self,
        name: str,
        description: str,
        continue_clip_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a persona for song generation.
        
        Args:
            name: Persona name
            description: Description of the persona
            continue_clip_id: Optional clip ID to base the persona on
            
        Returns:
            Dictionary with persona_id and other response data
        """
        if self.simulation_mode:
            logger.info("Simulation mode - returning mock persona")
            return {
                'persona_id': 'simulated-persona-id',
                'name': name,
                'description': description,
                'status': 'succeeded'
            }
        
        # Prepare payload
        payload = {
            'name': name,
            'description': description
        }
        
        if continue_clip_id:
            payload['continue_clip_id'] = continue_clip_id
        
        # Make the API request
        url = f"{self.base_url}/api/v1/sonic/persona"
        logger.info(f"Creating persona at: {url}")
        
        try:
            response = httpx.post(url, json=payload, headers=self._get_headers())
            logger.info(f"Persona creation response: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error creating persona: {response.text}")
                return {
                    'error': response.text,
                    'status': 'failed'
                }
                
        except Exception as e:
            logger.error(f"Exception creating persona: {str(e)}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def create_cover(
        self,
        continue_clip_id: str,
        prompt: str,
        title: Optional[str] = None,
        style: Optional[str] = None,
        negative_tags: Optional[str] = None,
        make_instrumental: bool = False,
        mv: str = 'sonic-v4',
        gpt_description_prompt: Optional[str] = None,
        voice_gender: str = 'female'
    ) -> Dict[str, Any]:
        """
        Create a cover version of a song.
        
        Args:
            continue_clip_id: Original clip ID to base the cover on
            prompt: Lyrics or prompt for the song
            title: Song title
            style: Style tags (comma separated)
            negative_tags: Tags to avoid in generation
            make_instrumental: Whether to make an instrumental version
            mv: Music video generation type
            gpt_description_prompt: Description prompt for the song
            voice_gender: Voice gender for the song (female or male)
            
        Returns:
            Dictionary with task_id, message, and status
        """
        if self.simulation_mode:
            logger.info("Simulation mode - returning mock cover response")
            return {
                'task_id': 'simulated-cover-task-id',
                'message': 'Cover creation task initiated successfully (simulated)',
                'status': 'pending'
            }
        
        # Log the prompt
        logger.info(f"Creating cover with prompt: {prompt[:100]}...")
        
        # Prepare payload
        payload = {
            'task_type': 'cover_music',
            'custom_mode': True,
            'continue_clip_id': continue_clip_id,
            'prompt': prompt,
            'mv': mv,
            'make_instrumental': make_instrumental
        }
        
        # Add optional parameters if provided
        if title:
            payload['title'] = title
            
        # Add style tags and voice gender
        tags = []
        if style:
            tags.append(style)
        if voice_gender:
            tags.append(f"{voice_gender} voice")
        
        if tags:
            payload['tags'] = ', '.join(tags)
            
        if negative_tags:
            payload['negative_tags'] = negative_tags
            
        if gpt_description_prompt and len(gpt_description_prompt) <= 199:
            payload['gpt_description_prompt'] = gpt_description_prompt
        
        # Make the API request
        url = f"{self.base_url}/api/v1/sonic/create"
        logger.info(f"Sending cover request to: {url}")
        
        try:
            response = httpx.post(url, json=payload, headers=self._get_headers())
            logger.info(f"Cover creation response: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                task_id = response_data.get('task_id')
                logger.info(f"Cover creation task initiated with ID: {task_id}")
                
                return {
                    'task_id': task_id,
                    'message': 'Cover creation task initiated successfully',
                    'status': 'pending'
                }
            else:
                logger.error(f"Error creating cover: {response.text}")
                return {
                    'error': response.text,
                    'status': 'failed'
                }
                
        except Exception as e:
            logger.error(f"Exception creating cover: {str(e)}")
            return {
                'error': str(e),
                'status': 'failed'
            } 