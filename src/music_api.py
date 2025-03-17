"""
Integration with MusicAPI.ai for creating music.
"""
import os
import json
import httpx
from dotenv import load_dotenv
from config.config import MUSICAPI_KEY, MUSICAPI_BASE_URL, DEFAULT_SONG_PARAMETERS
import asyncio
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MusicAPI:
    """Class for interacting with MusicAPI.ai."""
    
    def __init__(self, simulation_mode=False):
        """Initialize the MusicAPI client."""
        # Get API key directly from environment variables
        self.api_key = os.getenv("MUSICAPI_KEY")
        self.base_url = "https://api.musicapi.ai"
        self.simulation_mode = simulation_mode
        
        # Log initialization
        if simulation_mode:
            logger.info("MusicAPI initialized in simulation mode")
        else:
            logger.info(f"MusicAPI initialized with live API (key: {self.api_key[:5]}...)")
            
        # Note about persona creation
        logger.info("NOTE: Persona creation is currently unstable according to MusicAPI support")
        logger.info("Using direct song generation without persona")
        
        if not self.api_key:
            logger.error("MusicAPI key not found in environment variables!")
            raise ValueError("MusicAPI key not found. Please check your .env file.")
    
    def create_song(self, prompt, style="kpop", title=None, negative_tags=None, make_instrumental=False, mv="sonic-v3-5", gpt_description_prompt=None):
        """
        Create a song directly using the MusicAPI.ai API
        
        Args:
            prompt (str): Lyrics or description for the song (< 3000 chars)
            style (str): Music style/tags (default: kpop)
            title (str, optional): Song title (< 80 chars)
            negative_tags (str, optional): Elements to avoid in the song
            make_instrumental (bool, optional): Whether to create an instrumental
            mv (str): Music model to use (sonic-v3-5 or sonic-v4)
            gpt_description_prompt (str, optional): Description of the music
            
        Returns:
            dict: Response from the API or simulated response
        """
        if self.simulation_mode:
            logger.info(f"SIMULATION: Creating song with prompt: {prompt}")
            return self._simulate_song_creation(prompt, style, title, mv)
        
        # Prepare the payload according to the API documentation
        payload = {
            "custom_mode": True,
            "prompt": prompt,
            "mv": mv,
            "make_instrumental": make_instrumental
        }
        
        # Add optional parameters
        if title:
            payload["title"] = title
        
        if style:
            payload["tags"] = style
            
        if negative_tags:
            payload["negative_tags"] = negative_tags
            
        if gpt_description_prompt:
            payload["gpt_description_prompt"] = gpt_description_prompt
        
        # Prepare headers with API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Log the request
        logger.info(f"Creating song with prompt: {prompt[:100]}...")
        logger.info(f"Using API key: {self.api_key}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload: {payload}")
        
        try:
            # Make the API request to the correct endpoint
            endpoint = f"{self.base_url}/api/v1/sonic/create"
            logger.info(f"Sending request to: {endpoint}")
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers
            )
            
            # Log the response status
            logger.info(f"Song creation response status: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                
                if task_id:
                    logger.info(f"Song creation task initiated with ID: {task_id}")
                    return {
                        "task_id": task_id,
                        "message": "Song creation task initiated successfully",
                        "status": "pending"
                    }
                else:
                    logger.error("No task_id in response")
                    return {"error": "No task_id in response", "status": response.status_code}
            else:
                logger.error(f"Error creating song: {response.text}")
                return {"error": response.text, "status": response.status_code}
                
        except Exception as e:
            logger.error(f"Exception during song creation: {str(e)}")
            return {"error": str(e)}
    
    def get_song_status(self, task_id):
        """
        Check the status of a song creation task
        
        Args:
            task_id (str): The task ID returned from create_song
            
        Returns:
            dict: The status of the song creation task
        """
        if self.simulation_mode:
            logger.info(f"SIMULATION: Checking status for task: {task_id}")
            return {
                "status": "succeeded",
                "task_id": task_id,
                "audio_url": "https://example.com/simulated_song.mp3"
            }
            
        # Prepare headers with API key
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # Make the API request to check status using the correct endpoint format
            endpoint = f"{self.base_url}/api/v1/sonic/task/{task_id}"
            logger.info(f"Checking status at: {endpoint}")
            
            response = requests.get(
                endpoint,
                headers=headers
            )
            
            # Log the response status
            logger.info(f"Song status check response: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                
                # Extract relevant information from the response
                if result.get("code") == 200 and result.get("data"):
                    data_array = result.get("data")
                    
                    # First check if any song has succeeded
                    for song_data in data_array:
                        if song_data.get("state") == "succeeded":
                            return {
                                "status": "succeeded",
                                "task_id": task_id,
                                "audio_url": song_data.get("audio_url"),
                                "title": song_data.get("title"),
                                "lyrics": song_data.get("lyrics"),
                                "image_url": song_data.get("image_url"),
                                "video_url": song_data.get("video_url"),
                                "duration": song_data.get("duration"),
                                "created_at": song_data.get("created_at")
                            }
                    
                    # If no succeeded songs, return the first song's status
                    first_song = data_array[0]
                    return {
                        "status": first_song.get("state"),  # "pending", "running", or "succeeded"
                        "task_id": task_id,
                        "audio_url": first_song.get("audio_url"),
                        "title": first_song.get("title"),
                        "lyrics": first_song.get("lyrics"),
                        "image_url": first_song.get("image_url"),
                        "video_url": first_song.get("video_url"),
                        "duration": first_song.get("duration"),
                        "created_at": first_song.get("created_at")
                    }
                else:
                    logger.error(f"Invalid response format: {result}")
                    return {"error": "Invalid response format", "status": "failed"}
            elif response.status_code == 202:
                # Task is not ready yet, but this is expected behavior
                logger.info(f"Task {task_id} is still processing")
                return {
                    "status": "pending",
                    "task_id": task_id,
                    "message": "Task is still processing"
                }
            else:
                logger.error(f"Error checking song status: {response.text}")
                return {"error": response.text, "status": response.status_code}
                
        except Exception as e:
            logger.error(f"Exception during song status check: {str(e)}")
            return {"error": str(e)}
    
    def _simulate_song_creation(self, prompt, style, title, mv):
        """
        Simulate song creation for testing without API calls
        
        Args:
            prompt (str): Lyrics or description for the song
            style (str): Music style/tags
            title (str): Song title
            mv (str): Music model
            
        Returns:
            dict: Simulated API response
        """
        logger.info("Generating simulated song response")
        
        # Create a simulated response
        return {
            "task_id": "sim_task_12345",
            "message": "success",
            "status": "pending"
        }
    
    # Legacy method - kept for compatibility but will use simulation
    def create_persona(self, name, description, continue_clip_id=None):
        """
        Create a persona (NOTE: Currently unstable according to MusicAPI support)
        This method now returns a simulated response since the feature is unstable
        
        Args:
            name (str): Name of the persona
            description (str): Description of the persona
            continue_clip_id (str, optional): ID of a clip to continue from
            
        Returns:
            dict: Simulated response
        """
        logger.warning("Persona creation is currently unstable - returning simulated response")
        
        # Return a simulated persona response
        return {
            "id": f"sim_persona_{name.lower().replace(' ', '_')}",
            "name": name,
            "description": description,
            "status": "simulated",
            "message": "Persona creation is currently unstable according to MusicAPI support"
        }

    async def create_song_with_persona(self, persona_id, prompt, style="kpop", parameters=None, title=None):
        """
        Create a song on MusicAPI.ai using a persona.
        
        Args:
            persona_id (str): The ID of the persona to use
            prompt (str): The lyrics or prompt for the song
            style (str, optional): The style/tags of the song (e.g., "kpop")
            parameters (dict, optional): Additional parameters for the song
            title (str, optional): The title of the song
        
        Returns:
            dict: The created song data
        """
        if not self.api_key:
            # Simulate a response
            print(f"Simulated: Created song with prompt '{prompt}' on MusicAPI.ai")
            return {
                "id": "simulated-song-id",
                "audio_url": "https://example.com/simulated-song.mp3",
                "lyrics": "Simulated lyrics for the song"
            }
        
        # Prepare the payload according to the API documentation
        payload = {
            "task_type": "persona_music",
            "custom_mode": True,
            "prompt": prompt,
            "persona_id": persona_id,
            "mv": "sonic-v3-5"  # Using the default model
        }
        
        # Add optional parameters
        if title:
            payload["title"] = title
        
        if style:
            payload["tags"] = style
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with httpx.AsyncClient() as client:
            # First, create the song task
            response = await client.post(
                f"{self.base_url}/api/v1/sonic/create",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                
                if not task_id:
                    raise Exception("No task_id returned from API")
                
                # Now we need to poll for the result using the task_id
                # This is a simplified version - in a real implementation, you would
                # implement proper polling with timeouts and error handling
                max_attempts = 30
                for attempt in range(max_attempts):
                    # Wait a bit before checking
                    await asyncio.sleep(30)  # Changed from 5 to 30 seconds
                    
                    # Check the status of the task using the correct endpoint
                    status_response = await client.get(
                        f"{self.base_url}/api/v1/sonic/task/{task_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        # Check if the task is complete
                        if status_data.get("code") == 200 and status_data.get("data"):
                            data_array = status_data.get("data")
                            
                            # First check if any song has succeeded
                            for song_data in data_array:
                                if song_data.get("state") == "succeeded":
                                    # Return the song data
                                    return {
                                        "id": task_id,
                                        "audio_url": song_data.get("audio_url"),
                                        "lyrics": song_data.get("lyrics"),
                                        "title": song_data.get("title"),
                                        "image_url": song_data.get("image_url"),
                                        "video_url": song_data.get("video_url"),
                                        "duration": song_data.get("duration"),
                                        "created_at": song_data.get("created_at")
                                    }
                            
                            # If no succeeded songs, check if any have failed
                            for song_data in data_array:
                                if song_data.get("state") == "failed":
                                    raise Exception(f"Task failed: {song_data}")
                            
                            # If neither succeeded nor failed, continue polling
                
                # If we've reached here, the task didn't complete in time
                raise Exception(f"Task {task_id} did not complete in time")
            else:
                raise Exception(f"Error creating song: {response.text}") 