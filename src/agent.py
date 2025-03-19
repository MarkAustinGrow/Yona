#!/usr/bin/env python
"""
YonaAgent - Agentic AI K-pop Star

This module implements the YonaAgent class, which serves as the brain for Yona,
an agentic AI K-pop star. The agent uses OpenAI for decision-making and
interfaces with MusicAPI and SupabaseClient to create and manage songs.
"""
import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Union

import openai
from openai import OpenAI

from src.music_api import MusicAPI
from src.supabase_client import SupabaseClient
from src.config.config import OPENAI_KEY, OPENAI_MODEL, YONA_PERSONA

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YonaAgent:
    """
    YonaAgent is the brain of Yona, an agentic AI K-pop star.
    
    It uses OpenAI for decision-making and interfaces with MusicAPI and
    SupabaseClient to create and manage songs.
    """
    
    def __init__(self, openai_api_key=None, simulation_mode=False):
        """
        Initialize the YonaAgent.
        
        Args:
            openai_api_key: API key for OpenAI. If None, uses OPENAI_KEY from config.
            simulation_mode: If True, runs in simulation mode without making API calls.
        """
        self.simulation_mode = simulation_mode
        
        # Initialize OpenAI client
        self.openai_api_key = openai_api_key or OPENAI_KEY
        if not self.openai_api_key:
            logger.warning("OpenAI API key not provided. Agent will run in limited mode.")
        else:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Initialize tool connections
        self.music_api = MusicAPI(simulation_mode=simulation_mode)
        self.supabase_client = SupabaseClient(simulation_mode=simulation_mode)
        
        # Set up agent parameters
        self.persona = YONA_PERSONA
        
        logger.info("YonaAgent initialized")
    
    def generate_song_concept(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a song concept based on a prompt.
        
        Args:
            prompt: User prompt describing the song concept.
            
        Returns:
            Dictionary containing the song concept with keys like title, theme, mood, etc.
            and additional parameters for song creation.
        """
        logger.info(f"Generating song concept from prompt: {prompt}")
        
        if self.simulation_mode:
            logger.info("Simulation mode: Returning mock song concept")
            return {
                "title": "Simulated Song",
                "theme": "Imagination",
                "mood": "Upbeat",
                "musical_elements": "Electronic, Pop",
                "lyrics_concept": "A song about creating something from nothing",
                "style_tags": "kpop, electronic, upbeat",
                "negative_tags": "dark, heavy metal, sad",
                "make_instrumental": False,
                "mv_type": "sonic-v4",
                "description": "An upbeat electronic pop song about imagination and creativity"
            }
        
        try:
            # Use OpenAI to generate a song concept with additional parameters
            system_message = f"""
            You are Yona, a K-pop songwriter. Generate a detailed song concept based on the user's prompt.
            Return a JSON object with the following fields:
            - title: The title of the song
            - theme: The main theme or topic of the song
            - mood: The emotional mood of the song
            - musical_elements: Key musical elements or genre influences
            - lyrics_concept: A brief description of what the lyrics should convey
            - style_tags: Comma-separated style tags for the song (e.g., "kpop, electronic, bright")
            - negative_tags: Comma-separated tags to avoid in generation (e.g., "dark, heavy metal")
            - make_instrumental: Boolean indicating if the song should be instrumental (usually false)
            - mv_type: Music video generation type (one of: "sonic-v4", "sonic-v3", "none")
            - description: A brief description of the song (max 199 characters)
            
            Your response should be ONLY the JSON object, nothing else.
            """
            
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            concept_text = response.choices[0].message.content
            concept = json.loads(concept_text)
            
            logger.info(f"Generated song concept: {json.dumps(concept, indent=2)}")
            return concept
            
        except Exception as e:
            logger.error(f"Error generating song concept: {str(e)}")
            # Fallback to a basic concept with default parameters
            return {
                "title": prompt[:30] + "...",
                "theme": prompt,
                "mood": "Neutral",
                "musical_elements": "K-pop",
                "lyrics_concept": prompt,
                "style_tags": "kpop, pop",
                "negative_tags": "dark, heavy",
                "make_instrumental": False,
                "mv_type": "sonic-v4",
                "description": f"A K-pop song about {prompt[:50]}..."
            }
    
    def generate_lyrics(self, concept: Dict[str, Any]) -> str:
        """
        Generate lyrics based on a song concept.
        
        Args:
            concept: Dictionary containing the song concept.
            
        Returns:
            String containing the generated lyrics.
        """
        logger.info(f"Generating lyrics for concept: {concept.get('title', 'Untitled')}")
        
        if self.simulation_mode:
            logger.info("Simulation mode: Returning mock lyrics")
            return "This is a simulated song\nWith simulated lyrics\nFor a simulated world\n"
        
        try:
            # Extract key elements from the concept
            title = concept.get('title', 'Untitled')
            theme = concept.get('theme', '')
            mood = concept.get('mood', '')
            lyrics_concept = concept.get('lyrics_concept', '')
            
            # Use OpenAI to generate lyrics
            system_message = f"""
            You are Yona, a K-pop songwriter. Generate lyrics for a song based on the provided concept.
            The lyrics should be structured with verses, chorus, and optionally a bridge.
            Make the lyrics creative, emotional, and fitting for a K-pop song.
            
            Your response should be ONLY the lyrics, nothing else.
            """
            
            user_message = f"""
            Song Title: {title}
            Theme: {theme}
            Mood: {mood}
            Lyrics Concept: {lyrics_concept}
            
            Please generate complete lyrics for this song.
            """
            
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Get the lyrics from the response
            lyrics = response.choices[0].message.content.strip()
            
            logger.info(f"Generated lyrics (excerpt): {lyrics[:100]}...")
            return lyrics
            
        except Exception as e:
            logger.error(f"Error generating lyrics: {str(e)}")
            # Fallback to a template
            title = concept.get('title', 'Untitled Song')
            theme = concept.get('theme', 'Unknown theme')
            mood = concept.get('mood', 'Neutral mood')
            
            return f"""[Verse 1]
This is a song about {theme}
With a {mood} feeling throughout

[Chorus]
{title}, {title}
The main idea from the concept
{title}, {title}
Expressing the emotions intended

[Verse 2]
More details about {theme}
Continuing the {mood} feeling

[Chorus]
{title}, {title}
The main idea from the concept
{title}, {title}
Expressing the emotions intended

[Bridge]
A different perspective
About {theme}

[Chorus]
{title}, {title}
The main idea from the concept
{title}, {title}
Expressing the emotions intended

[Outro]
Final thoughts about {theme}
"""
    
    def create_song(self, title: str, lyrics: str, style: Optional[str] = None, 
                   negative_tags: Optional[str] = None, make_instrumental: bool = False,
                   mv: str = 'sonic-v4', gpt_description_prompt: Optional[str] = None,
                   voice_gender: str = 'female', max_attempts: int = 60,
                   check_interval: int = 30) -> Dict[str, Any]:
        """
        Create a song using the MusicAPI.
        
        Args:
            title: Title of the song
            lyrics: Lyrics for the song
            style: Style tags for the song
            negative_tags: Negative tags to avoid
            make_instrumental: Whether to make the song instrumental
            mv: Music video generation type
            gpt_description_prompt: Description prompt for GPT
            voice_gender: Voice gender for the song
            max_attempts: Maximum number of status check attempts
            check_interval: Time in seconds between status checks
            
        Returns:
            Dictionary containing the song data, including URLs and metadata.
        """
        logger.info(f"Creating song: {title}")
        
        if self.simulation_mode:
            logger.info("Simulation mode: Returning mock song data")
            return {
                "title": title,
                "audio_url": "https://example.com/simulated-audio.mp3",
                "video_url": "https://example.com/simulated-video.mp4",
                "image_url": "https://example.com/simulated-image.jpg",
                "status": "succeeded"
            }
        
        try:
            # Create the song using MusicAPI
            result = self.music_api.create_song(
                prompt=lyrics,
                title=title,
                style=style,
                negative_tags=negative_tags,
                make_instrumental=make_instrumental,
                mv=mv,
                gpt_description_prompt=gpt_description_prompt[:199] if gpt_description_prompt else None,
                voice_gender=voice_gender
            )
            
            if result.get('status') == 'failed':
                logger.error(f"Failed to create song: {result.get('error')}")
                return result
                
            logger.info(f"Song creation initiated: {result}")
            
            # Check song status until it's completed or failed
            task_id = result.get('task_id')
            if not task_id:
                logger.error("Failed to get task ID for song creation")
                return {"status": "failed", "error": "No task ID returned"}
            
            # Poll for song status
            logger.info(f"Checking status for task: {task_id}")
            status = "pending"
            attempt = 1
            song_data = None
            
            while status != "succeeded" and status != "failed" and attempt <= max_attempts:
                logger.info(f"Checking song status (attempt {attempt}/{max_attempts})...")
                status_response = self.music_api.check_song_status(task_id)
                
                # Get the first item in the data array (assuming it's the main song)
                if status_response and 'data' in status_response and len(status_response['data']) > 0:
                    song_data = status_response['data'][0]
                    status = song_data.get('state', 'unknown')
                    
                    # If we have audio_url but status is still pending, we can proceed
                    if status == "pending" and song_data.get('audio_url') and song_data.get('audio_url').startswith('https://'):
                        logger.info("Song has audio URL but status is still pending. Proceeding anyway.")
                        status = "succeeded"
                
                if status not in ["succeeded", "failed"]:
                    logger.info(f"Song is still being processed (attempt {attempt}/{max_attempts})...")
                    attempt += 1
                    time.sleep(check_interval)  # Wait between checks
            
            if status == "succeeded" or (status == "pending" and song_data and song_data.get('audio_url')):
                logger.info(f"Song status: {status}")
                
                # Extract data from the response
                audio_url = song_data.get('audio_url', '')
                video_url = song_data.get('video_url', '')
                image_url = song_data.get('image_url', '')
                duration = song_data.get('duration', 0)
                
                logger.info(f"Audio URL: {audio_url}")
                
                # Create params_used object
                params_used = {
                    'prompt': lyrics,
                    'title': title,
                    'style': style,
                    'negative_tags': negative_tags,
                    'make_instrumental': make_instrumental,
                    'mv': mv,
                    'gpt_description_prompt': gpt_description_prompt[:199] if gpt_description_prompt else None,
                    'voice_gender': voice_gender
                }
                
                # Prepare song data for storage
                song_data_for_db = {
                    'title': title,
                    'lyrics': lyrics,
                    'style': style,
                    'audio_url': audio_url,
                    'video_url': video_url,
                    'image_url': image_url,
                    'make_instrumental': make_instrumental,
                    'mv': mv,
                    'gpt_description': gpt_description_prompt[:199] if gpt_description_prompt else None,
                    'negative_tags': negative_tags,
                    'duration': duration,
                    'persona_id': 'direct_generation',  # Use direct_generation as we're not using a persona
                    'params_used': params_used  # Add the params_used field
                }
                
                # Store song data in Supabase
                db_song_id = self.supabase_client.store_song_data(song_data_for_db)
                
                if db_song_id:
                    logger.info(f"Song data stored in Supabase: {db_song_id}")
                    song_data_for_db['id'] = db_song_id
                    song_data_for_db['status'] = status
                    return song_data_for_db
                else:
                    logger.warning("Failed to store song data in Supabase")
                    song_data['status'] = status
                    return song_data
                
            else:
                logger.error(f"Song creation failed with status: {status}")
                if song_data and 'error' in song_data:
                    error_details = song_data['error']
                else:
                    error_details = "Song creation timed out or failed without error details"
                
                return {
                    "status": "failed",
                    "error": error_details,
                    "last_data": song_data
                }
                
        except Exception as e:
            logger.error(f"Error in song creation process: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def list_songs(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List songs from the database.
        
        Args:
            limit: Maximum number of songs to return
            offset: Offset for pagination
            
        Returns:
            List of dictionaries containing song data
        """
        logger.info(f"Listing songs (limit: {limit}, offset: {offset})")
        
        if self.simulation_mode:
            logger.info("Simulation mode: Returning mock song list")
            return [
                {
                    "id": "sim-1",
                    "title": "Simulated Song 1",
                    "audio_url": "https://example.com/sim1.mp3"
                },
                {
                    "id": "sim-2",
                    "title": "Simulated Song 2",
                    "audio_url": "https://example.com/sim2.mp3"
                }
            ]
        
        try:
            # Get songs from Supabase
            songs = self.supabase_client.list_songs(limit=limit, offset=offset)
            logger.info(f"Retrieved {len(songs)} songs from database")
            return songs
        except Exception as e:
            logger.error(f"Error listing songs: {str(e)}")
            return []
    
    def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process a natural language request from the user and take appropriate action.
        
        Args:
            user_input: String containing the user's request
            
        Returns:
            Dictionary with results and response
        """
        logger.info(f"Processing user request: {user_input}")
        
        try:
            # Use OpenAI to analyze the request
            analysis = self._analyze_request(user_input)
            
            # Determine the intent and extract parameters
            intent = analysis.get('intent')
            params = analysis.get('parameters', {})
            
            logger.info(f"Detected intent: {intent}")
            logger.info(f"Extracted parameters: {json.dumps(params, indent=2)}")
            
            # Execute the appropriate action based on intent
            if intent == 'create_song':
                # Generate concept if not provided
                if 'concept' not in params:
                    concept = self.generate_song_concept(params.get('prompt', user_input))
                else:
                    concept = params['concept']
                    
                # Generate lyrics if not provided
                if 'lyrics' not in params:
                    lyrics = self.generate_lyrics(concept)
                else:
                    lyrics = params['lyrics']
                    
                # Extract parameters from the LLM-generated concept
                style_tags = concept.get('style_tags')
                negative_tags = concept.get('negative_tags')
                make_instrumental = concept.get('make_instrumental', False)
                mv_type = concept.get('mv_type', 'sonic-v4')
                description = concept.get('description', '')
                
                # Create params_used object
                params_used = {
                    'prompt': lyrics,
                    'title': concept.get('title'),
                    'style': style_tags,
                    'negative_tags': negative_tags,
                    'make_instrumental': make_instrumental,
                    'mv': mv_type,
                    'gpt_description_prompt': description,
                    'voice_gender': 'female',  # Hard-coded as female
                    'original_prompt': user_input,
                    'concept': concept  # Include the full LLM-generated concept
                }
                
                # Create the song with hard-coded female voice
                result = self.create_song(
                    title=concept.get('title'),
                    lyrics=lyrics,
                    style=style_tags,
                    negative_tags=negative_tags,
                    make_instrumental=make_instrumental,
                    mv=mv_type,
                    gpt_description_prompt=description,
                    voice_gender="female"  # Hard-coded as female
                )
                
                # Add params_used to the result if successful
                if result.get('status') != 'failed':
                    result['params_used'] = params_used
                
                if result.get('status') == 'failed':
                    return {
                        'action': 'create_song',
                        'result': result,
                        'response': f"I couldn't create the song. Error: {result.get('error')}"
                    }
                
                return {
                    'action': 'create_song',
                    'result': result,
                    'response': f"I've created a song titled '{concept.get('title')}'. You can listen to it at {result.get('audio_url')}"
                }
                
            elif intent == 'list_songs':
                # Retrieve songs from database
                songs = self.list_songs(limit=params.get('limit', 10), offset=params.get('offset', 0))
                
                song_list_text = "\n".join([f"- {song.get('title')}: {song.get('audio_url')}" for song in songs])
                
                return {
                    'action': 'list_songs',
                    'result': songs,
                    'response': f"I found {len(songs)} songs in the database:\n{song_list_text}"
                }
            
            elif intent == 'get_song':
                # Get a specific song by ID
                song_id = params.get('song_id')
                if not song_id:
                    return {
                        'action': 'get_song',
                        'result': None,
                        'response': "I need a song ID to retrieve a specific song."
                    }
                
                song = self.supabase_client.get_song_by_id(song_id)
                
                if not song:
                    return {
                        'action': 'get_song',
                        'result': None,
                        'response': f"I couldn't find a song with ID {song_id}."
                    }
                
                return {
                    'action': 'get_song',
                    'result': song,
                    'response': f"Here's the song '{song.get('title')}'. You can listen to it at {song.get('audio_url')}"
                }
            
            else:
                return {
                    'action': 'unknown',
                    'result': None,
                    'response': "I'm not sure how to help with that request. You can ask me to create a song, list songs, or get a specific song."
                }
                
        except Exception as e:
            logger.error(f"Error processing user request: {str(e)}")
            return {
                'action': 'error',
                'result': None,
                'response': f"I encountered an error while processing your request: {str(e)}"
            }
    
    def _analyze_request(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze a user request to determine intent and extract parameters.
        
        Args:
            user_input: String containing the user's request
            
        Returns:
            Dictionary with intent and parameters
        """
        # In simulation mode, use a simple rule-based approach
        if self.simulation_mode:
            # Basic intent detection based on keywords
            if "create" in user_input.lower() and "song" in user_input.lower():
                return {"intent": "create_song", "parameters": {"prompt": user_input}}
            elif "list" in user_input.lower() and "song" in user_input.lower():
                return {"intent": "list_songs", "parameters": {"limit": 10}}
            elif "get" in user_input.lower() and "song" in user_input.lower():
                # Try to extract an ID if present
                import re
                id_match = re.search(r'id\s+(\w+)', user_input.lower())
                song_id = id_match.group(1) if id_match else None
                return {"intent": "get_song", "parameters": {"song_id": song_id}}
            else:
                return {"intent": "unknown", "parameters": {}}
        
        # For non-simulation mode, use OpenAI
        system_message = """
        You are an assistant that analyzes user requests and extracts structured information.
        Determine the user's intent and extract relevant parameters.
        
        Possible intents:
        - create_song: User wants to create a new song
        - list_songs: User wants to list existing songs
        - get_song: User wants to retrieve a specific song
        
        Return a JSON object with:
        - intent: The detected intent
        - parameters: An object containing extracted parameters
        
        Your response should be ONLY the JSON object, nothing else.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ]
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            analysis = json.loads(analysis_text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing request: {str(e)}")
            # Fallback to a basic analysis
            if "create" in user_input.lower() and "song" in user_input.lower():
                return {"intent": "create_song", "parameters": {"prompt": user_input}}
            elif "list" in user_input.lower() and "song" in user_input.lower():
                return {"intent": "list_songs", "parameters": {}}
            else:
                return {"intent": "unknown", "parameters": {}}
