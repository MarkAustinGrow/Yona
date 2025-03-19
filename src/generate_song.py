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
    
    # Optional arguments - now used to override LLM-generated parameters if desired
    parser.add_argument('--override-style', help='Override LLM-generated style tags')
    parser.add_argument('--override-negative-tags', help='Override LLM-generated negative tags')
    parser.add_argument('--override-instrumental', action='store_true', help='Override LLM decision on instrumental')
    parser.add_argument('--override-mv', help='Override LLM-generated music video type')
    parser.add_argument('--override-description', help='Override LLM-generated description')
    parser.add_argument('--max-attempts', type=int, default=60, help='Maximum number of status check attempts')
    parser.add_argument('--check-interval', type=int, default=30, help='Time in seconds between status checks')
    parser.add_argument('--simulation', action='store_true', help='Run in simulation mode (no API calls)')
    
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
    if not OPENAI_KEY and not args.simulation:
        logger.warning("OpenAI API key is missing. Set OPENAI_KEY in .env or use --simulation")
    
    if not MUSICAPI_KEY and not args.simulation:
        logger.error("MusicAPI key is missing. Set MUSICAPI_KEY in .env or use --simulation")
        return 1
    
    # Initialize the agent
    logger.info("Initializing YonaAgent")
    agent = YonaAgent(simulation_mode=args.simulation)
    
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
        music_api = MusicAPI(simulation_mode=args.simulation)
        
        # Create the song with hard-coded female voice
        logger.info(f"Creating song: {title}")
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
        
        while status != "succeeded" and status != "failed" and attempt <= max_attempts:
            logger.info(f"Checking song status (attempt {attempt}/{max_attempts})...")
            status_response = music_api.check_song_status(task_id)
            
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
            supabase_client = SupabaseClient(simulation_mode=args.simulation)
            
            # Create a params_used object with all parameters
            params_used = {
                'prompt': lyrics,
                'title': title,
                'style': style_tags,
                'negative_tags': negative_tags,
                'make_instrumental': make_instrumental,
                'mv': mv_type,
                'gpt_description_prompt': description[:199] if description else None,
                'voice_gender': 'female',  # Hard-coded as female
                'original_prompt': args.prompt,
                'concept': concept  # Include the full LLM-generated concept
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
                'original_prompt': args.prompt,
                'song_concept': json.dumps(concept),
                'persona_id': 'direct_generation',  # Use direct_generation as we're not using a persona
                'params_used': params_used  # Add the params_used field
            }
            
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
