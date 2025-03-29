#!/usr/bin/env python
"""
Song Generation Script for Yona

This script uses the YonaAgent to generate a song concept and lyrics from a simple prompt,
then uses the MusicAPI to create the actual song.
"""
import os
import sys
import time
import json
import logging
import argparse
import tempfile
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import YonaAgent
from src.music_api import MusicAPI
from src.supabase_client import SupabaseClient
from src.config.config import MUSICAPI_KEY, OPENAI_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a song using YonaAgent and MusicAPI')
    
    # Required arguments
    parser.add_argument('prompt', help='Prompt describing the song to create')
    
    # API selection
    parser.add_argument('--api', choices=['sonic', 'nuro'], default='sonic', 
                        help='API to use for song generation (default: sonic)')
    
    # Sonic API parameters (used when --api=sonic)
    parser.add_argument('--override-style', help='Override LLM-generated style tags (Sonic API)')
    parser.add_argument('--override-negative-tags', help='Override LLM-generated negative tags (Sonic API)')
    parser.add_argument('--override-instrumental', action='store_true', help='Override LLM decision on instrumental (Sonic API)')
    parser.add_argument('--override-mv', help='Override LLM-generated music video type (Sonic API)')
    parser.add_argument('--override-description', help='Override LLM-generated description (Sonic API)')
    
    # Nuro API parameters (used when --api=nuro)
    parser.add_argument('--gender', choices=['Female', 'Male'], help="Singer's gender (Nuro API)")
    parser.add_argument('--genre', help="Genre of the song (Nuro API)")
    parser.add_argument('--mood', help="Mood of the song (Nuro API)")
    parser.add_argument('--timbre', help="Timbre of the song (Nuro API)")
    parser.add_argument('--duration', type=int, help="Duration in seconds, 30-240 (Nuro API)")
    
    # Common parameters
    parser.add_argument('--max-attempts', type=int, default=60, help='Maximum number of status check attempts')
    parser.add_argument('--check-interval', type=int, default=30, help='Time in seconds between status checks')
    
    return parser.parse_args()

def generate_lyrics_from_concept(concept: Dict[str, Any], agent: YonaAgent) -> str:
    """
    Generate lyrics based on a song concept.
    
    Args:
        concept: The song concept dictionary with title, theme, mood, etc.
        agent: The YonaAgent instance to use for lyrics generation
        
    Returns:
        The generated lyrics as a string
    """
    logger.info(f"Generating lyrics for concept: {concept['title']}")
    
    # Use the agent to generate lyrics based on the concept
    lyrics = agent.generate_lyrics(concept)
    logger.info(f"Generated lyrics (excerpt): {lyrics[:100]}...")
    
    return lyrics

def main():
    """Main function to generate and create a song."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    # Check if required API keys are available
    if not OPENAI_KEY:
        logger.error("OpenAI API key is missing. Set OPENAI_KEY in .env")
        return 1
    
    if not MUSICAPI_KEY:
        logger.error("MusicAPI key is missing. Set MUSICAPI_KEY in .env")
        return 1
    
    # Initialize the agent
    logger.info("Initializing YonaAgent")
    agent = YonaAgent()
    
    try:
        # Generate song concept
        logger.info(f"Generating song concept from prompt: {args.prompt}")
        concept = agent.generate_song_concept(args.prompt)
        
        logger.info(f"Generated song concept: {json.dumps(concept, indent=2)}")
        
        # Extract the title
        title = concept.get('title', 'Generated Song')
        logger.info(f"Song title: {title}")
        
        # Generate lyrics based on the concept
        lyrics = generate_lyrics_from_concept(concept, agent)
        
        # Save lyrics to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(lyrics)
            lyrics_file = temp_file.name
        
        logger.info(f"Lyrics saved to temporary file: {lyrics_file}")
        
        # Extract parameters from the LLM-generated concept
        style_tags = concept.get('style_tags')
        negative_tags = concept.get('negative_tags')
        make_instrumental = concept.get('make_instrumental', False)
        mv_type = concept.get('mv_type', 'sonic-v4')
        description = concept.get('description', '')
        
        # Apply overrides if provided
        if args.override_style:
            style_tags = args.override_style
        if args.override_negative_tags:
            negative_tags = args.override_negative_tags
        if args.override_instrumental:
            make_instrumental = True
        if args.override_mv:
            mv_type = args.override_mv
        if args.override_description:
            description = args.override_description
        
        # Initialize MusicAPI
        music_api = MusicAPI()
        
        # Create the song using the selected API
        logger.info(f"Creating song: {title} using {args.api.upper()} API")
        
        if args.api == 'nuro':
            # Use Nuro API
            result = music_api.create_song_nuro(
                lyrics=lyrics,
                gender=args.gender,
                genre=args.genre,
                mood=args.mood,
                timbre=args.timbre,
                duration=args.duration
            )
        else:
            # Use Sonic API (default)
            result = music_api.create_song(
                prompt=lyrics,
                title=title,
                style=style_tags,
                negative_tags=negative_tags,
                make_instrumental=make_instrumental,
                mv=mv_type,
                gpt_description_prompt=description[:199],  # Limit to 199 characters
                voice_gender="female"  # Hard-coded as female
            )
            
            # Check if Sonic API is under maintenance, if so, fall back to Nuro API
            if result.get('status') == 'failed' and 'maintenance' in str(result.get('error', '')).lower():
                logger.warning("Sonic API is under maintenance, falling back to Nuro API")
                
                # Determine gender from voice_gender parameter
                voice_gender = "female"  # This was hard-coded above
                gender = "Female" if "female" in voice_gender.lower() else "Male"
                
                # Map style_tags to genre and mood if possible
                genre = "Pop"  # Default genre
                mood = "Happy"  # Default mood
                
                if style_tags:
                    style_lower = style_tags.lower()
                    # Simple mapping of common styles to genres
                    if "rock" in style_lower:
                        genre = "Rock"
                    elif "pop" in style_lower:
                        genre = "Pop"
                    elif "hip hop" in style_lower or "rap" in style_lower:
                        genre = "Hip Hop/Rap"
                    elif "r&b" in style_lower or "soul" in style_lower:
                        genre = "R&B/Soul"
                    elif "electronic" in style_lower:
                        genre = "Electronic"
                    
                    # Simple mapping of common styles to moods
                    if "upbeat" in style_lower or "happy" in style_lower:
                        mood = "Happy"
                    elif "energetic" in style_lower or "dynamic" in style_lower:
                        mood = "Dynamic/Energetic"
                    elif "sad" in style_lower or "melancholic" in style_lower:
                        mood = "Sentimental/Melancholic/Lonely"
                    elif "chill" in style_lower or "relaxing" in style_lower:
                        mood = "Chill"
                
                # Use Nuro API as fallback
                logger.info(f"Falling back to Nuro API with genre={genre}, mood={mood}, gender={gender}")
                result = music_api.create_song_nuro(
                    lyrics=lyrics,
                    gender=gender,
                    genre=genre,
                    mood=mood,
                    timbre=None,  # Use default
                    duration=None  # Use default
                )
                
                # Update args to reflect the fallback parameters for later use in params_used
                args.api = 'nuro'
                args.gender = gender
                args.genre = genre
                args.mood = mood
        
        # Clean up the temporary lyrics file
        try:
            os.unlink(lyrics_file)
            logger.info("Temporary lyrics file deleted")
        except:
            logger.warning("Could not delete temporary lyrics file")
        
        if result.get('status') == 'failed':
            logger.error(f"Failed to create song: {result.get('error')}")
            return 1
            
        logger.info(f"Song creation initiated: {result}")
        
        # Check song status until it's completed or failed
        task_id = result.get('task_id')
        if not task_id:
            logger.error("Failed to get task ID for song creation")
            return 1
        
        # Poll for song status
        logger.info(f"Checking status for task: {task_id}")
        status = "pending"
        attempt = 1
        max_attempts = args.max_attempts
        check_interval = args.check_interval
        song_data = None
        
        # Determine which API was used
        is_nuro_api = args.api == 'nuro' or result.get('api_used') == 'nuro'
        
        while status != "succeeded" and status != "failed" and attempt <= max_attempts:
            logger.info(f"Checking song status (attempt {attempt}/{max_attempts})...")
            
            # Use the appropriate status checking method based on the API
            if is_nuro_api:
                status_response = music_api.check_song_status_nuro(task_id)
            else:
                status_response = music_api.check_song_status(task_id)
            
            if is_nuro_api:
                # Handle Nuro API response format
                if status_response:
                    song_data = status_response
                    # Check both 'state' and 'status' fields (Nuro API uses 'status')
                    status = song_data.get('state', song_data.get('status', 'unknown'))
                    
                    # If we have audio_url but status is still pending, we can proceed
                    if status == "pending" and song_data.get('audio_url') and song_data.get('audio_url').startswith('https://'):
                        logger.info("Song has audio URL but status is still pending. Proceeding anyway.")
                        status = "succeeded"
                    
                    # If progress is 100%, consider it succeeded regardless of status
                    if song_data.get('progress') == 100:
                        logger.info("Song progress is 100%, considering it successful.")
                        status = "succeeded"
            else:
                # Handle Sonic API response format
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
            if status == "pending":
                logger.info("Song is still pending but has audio URL, considering it successful")
            else:
                logger.info("Song creation completed successfully!")
            
            # Extract data from the response
            audio_url = song_data.get('audio_url', '')
            video_url = song_data.get('video_url', '')
            image_url = song_data.get('image_url', '')
            duration = song_data.get('duration', 0)
            
            logger.info(f"Audio URL: {audio_url}")
            
            # Check if audio URL is valid
            if not audio_url or not audio_url.startswith('https://'):
                logger.warning("Audio URL is not valid, but continuing with storage")
            
            # Store the song data in Supabase
            supabase_client = SupabaseClient()
            
            # Create a params_used object with all parameters
            if is_nuro_api:
                # Nuro API parameters
                params_used = {
                    'api_used': 'nuro',
                    'lyrics': lyrics,
                    'gender': args.gender,
                    'genre': args.genre,
                    'mood': args.mood,
                    'timbre': args.timbre,
                    'duration': args.duration,
                    'prompt': args.prompt  # Store the prompt in a field that exists in the DB schema
                }
            else:
                # Sonic API parameters
                params_used = {
                    'api_used': 'sonic',
                    'prompt': lyrics,
                    'title': title,
                    'style': style_tags,
                    'negative_tags': negative_tags,
                    'make_instrumental': make_instrumental,
                    'mv': mv_type,
                    'gpt_description_prompt': description[:199] if description else None,
                    'voice_gender': 'female',  # Hard-coded as female
                    'user_prompt': args.prompt  # Store the prompt in a field that exists in the DB schema
                }
            
            # Prepare song data for storage
            song_data_for_db = {
                'title': title,
                'lyrics': lyrics,
                'style': style_tags,
                'audio_url': audio_url,
                'video_url': video_url,
                'image_url': image_url,
                'make_instrumental': make_instrumental,
                'mv': mv_type,
                'gpt_description': description[:199],
                'negative_tags': negative_tags,
                'duration': duration,
                'persona_id': 'direct_generation',  # Use direct_generation as we're not using a persona
                'params_used': params_used,  # Add the params_used field
                'api_used': 'nuro' if is_nuro_api else 'sonic'  # Add the api_used field
            }
            
            # Add Nuro-specific fields if using Nuro API
            if is_nuro_api and song_data:
                # Extract Nuro-specific fields from the response
                song_data_for_db['gender'] = song_data.get('gender')
                song_data_for_db['genre'] = song_data.get('genre')
                song_data_for_db['mood'] = song_data.get('mood')
                song_data_for_db['timbre'] = song_data.get('timbre')
            
            # Store song data in Supabase
            db_song_id = supabase_client.store_song_data(song_data_for_db)
            
            if db_song_id:
                logger.info(f"Song data stored in Supabase: {db_song_id}")
                logger.info(f"Successfully created song: {title} (ID: {db_song_id})")
                logger.info(f"Audio URL: {audio_url}")
                logger.info(f"Video URL: {video_url}")
                logger.info(f"Image URL: {image_url}")
            else:
                logger.warning("Failed to store song data in Supabase")
            
            return 0
            
        else:
            logger.error(f"Song creation failed with status: {status}")
            if song_data and 'error' in song_data:
                logger.error(f"Error details: {song_data['error']}")
            else:
                logger.error("Song creation timed out or failed without error details")
                logger.error(f"Last song data: {song_data}")
            
            return 1
            
    except Exception as e:
        logger.error(f"Error in song generation process: {str(e)}")
        logger.exception("Exception details:")
        return 1

if __name__ == "__main__":
    sys.exit(main())
