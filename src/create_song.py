"""
Script to create a new song with all available parameters from Suno/MusicAPI.ai.

Available parameters:
- custom_mode: boolean (required) - If you want to customize the lyrics, this should be true
- prompt: string (required) - Song lyrics, should be less than 3000 characters
- title: string (optional) - Song title, should be less than 80 characters
- tags/style: string (optional) - Song tags/style, should be less than 200 characters
- negative_tags: string (optional) - Elements you want to avoid in your songs
- mv: string (required) - Music model, which can be sonic-v3-5 or sonic-v4
- make_instrumental: boolean (optional) - Instrumental mode
- gpt_description_prompt: string (optional) - Description of the music
"""
import os
import json
import asyncio
from dotenv import load_dotenv
from supabase import create_client
from music_api import MusicAPI
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def store_song_data(title, persona_id, lyrics, audio_url, params_used):
    """Store song data in Supabase."""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials missing. Please check your .env file.")
        return None
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        
        # Prepare the data to insert
        song_data = {
            "title": title,
            "persona_id": persona_id,
            "lyrics": lyrics,
            "audio_url": audio_url,
            "params_used": json.dumps(params_used) if isinstance(params_used, dict) else params_used
        }
        
        # Insert the data into the songs table
        logger.info(f"Storing song data for '{title}' in Supabase")
        response = supabase.table("songs").insert(song_data).execute()
        
        # Check if the insert was successful
        if hasattr(response, 'data') and len(response.data) > 0:
            logger.info(f"Song data stored successfully with ID: {response.data[0]['id']}")
            return response.data[0]
        else:
            logger.error(f"Error storing song data")
            return None
            
    except Exception as e:
        logger.error(f"Exception during song data storage: {str(e)}")
        return None

async def create_song(lyrics, title, style="kpop", mv="sonic-v3-5", negative_tags=None, make_instrumental=False, description=None):
    """
    Create a new song with all available parameters.
    
    Args:
        lyrics (str): Song lyrics or description, should be less than 3000 characters
        title (str): Song title, should be less than 80 characters
        style (str): Music style/tags, should be less than 200 characters (default: "kpop")
        mv (str): Music model, either "sonic-v3-5" or "sonic-v4" (default: "sonic-v3-5")
        negative_tags (str): Elements to avoid in the song (default: None)
        make_instrumental (bool): Whether to create an instrumental version (default: False)
        description (str): Description of the music for the GPT model (default: None)
        
    Returns:
        dict: Song data if successful, None otherwise
    """
    # Initialize MusicAPI
    music_api = MusicAPI(simulation_mode=False)
    
    # Create the song
    logger.info(f"Creating new song: {title}")
    song_result = music_api.create_song(
        prompt=lyrics,
        style=style,
        title=title,
        mv=mv,
        negative_tags=negative_tags,
        make_instrumental=make_instrumental,
        gpt_description_prompt=description
    )
    
    # Check if song creation was initiated successfully
    if "error" in song_result:
        logger.error(f"Error creating song: {song_result['error']}")
        return None
    else:
        logger.info(f"Song creation initiated: {song_result}")
        
        # Poll for the song status
        task_id = song_result.get("task_id")
        if task_id:
            logger.info(f"Checking status for task: {task_id}")
            
            # Poll for the song status
            max_attempts = 30
            for attempt in range(max_attempts):
                logger.info(f"Checking song status (attempt {attempt+1}/{max_attempts})...")
                
                # Wait before checking
                await asyncio.sleep(30)
                
                # Check the status
                status_result = music_api.get_song_status(task_id)
                
                # Continue polling if we get a pending status
                if status_result.get("status") == "pending" or status_result.get("status") == "running":
                    logger.info(f"Song is still being processed (attempt {attempt+1}/{max_attempts})...")
                    continue
                
                if "error" in status_result:
                    logger.error(f"Error checking song status: {status_result['error']}")
                    break
                
                logger.info(f"Song status: {status_result.get('status')}")
                
                # If the song is ready, store it in Supabase
                if status_result.get("status") == "succeeded":
                    logger.info("Song creation completed successfully!")
                    logger.info(f"Audio URL: {status_result.get('audio_url')}")
                    
                    # Store song data in Supabase
                    params_used = {
                        "prompt": lyrics,
                        "style": style,
                        "title": title,
                        "mv": mv,
                        "negative_tags": negative_tags,
                        "make_instrumental": make_instrumental,
                        "gpt_description_prompt": description,
                        "image_url": status_result.get("image_url", ""),
                        "video_url": status_result.get("video_url", ""),
                        "duration": status_result.get("duration", 0),
                        "created_at": status_result.get("created_at", "")
                    }
                    
                    supabase_result = await store_song_data(
                        title=title,
                        persona_id="direct_generation",  # No persona used
                        lyrics=status_result.get("lyrics", lyrics),
                        audio_url=status_result.get("audio_url", ""),
                        params_used=params_used
                    )
                    
                    if supabase_result:
                        logger.info(f"Song data stored in Supabase: {supabase_result['id']}")
                        return supabase_result
                    else:
                        logger.error("Failed to store song data in Supabase")
                        return None
                
                # If the song failed, log the error
                if status_result.get("status") == "failed":
                    logger.error(f"Song creation failed: {status_result}")
                    return None
            
            logger.error(f"Song creation timed out after {max_attempts} attempts")
            return None

async def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Create a new song with all available Suno/MusicAPI.ai parameters')
    parser.add_argument('--title', type=str, required=True, help='Song title (< 80 characters)')
    parser.add_argument('--lyrics', type=str, help='Song lyrics (< 3000 characters)')
    parser.add_argument('--style', type=str, default='kpop', help='Music style/tags (< 200 characters)')
    parser.add_argument('--mv', type=str, default='sonic-v3-5', choices=['sonic-v3-5', 'sonic-v4'], help='Music model')
    parser.add_argument('--negative-tags', type=str, help='Elements to avoid in the song')
    parser.add_argument('--instrumental', action='store_true', help='Create an instrumental version')
    parser.add_argument('--description', type=str, help='Description of the music for the GPT model')
    parser.add_argument('--lyrics-file', type=str, help='Path to a file containing the lyrics')
    
    args = parser.parse_args()
    
    # Get lyrics from file if specified
    if args.lyrics_file:
        try:
            with open(args.lyrics_file, 'r') as f:
                lyrics = f.read()
        except Exception as e:
            logger.error(f"Error reading lyrics file: {str(e)}")
            return
    elif args.lyrics:
        lyrics = args.lyrics
    else:
        logger.error("Either --lyrics or --lyrics-file must be provided")
        parser.print_help()
        return
    
    # Validate input lengths
    if len(lyrics) > 3000:
        logger.warning(f"Lyrics exceed 3000 characters ({len(lyrics)}). This may cause issues with the API.")
    
    if args.title and len(args.title) > 80:
        logger.warning(f"Title exceeds 80 characters ({len(args.title)}). This may cause issues with the API.")
    
    if args.style and len(args.style) > 200:
        logger.warning(f"Style/tags exceed 200 characters ({len(args.style)}). This may cause issues with the API.")
    
    # Create the song
    result = await create_song(
        lyrics=lyrics,
        title=args.title,
        style=args.style,
        mv=args.mv,
        negative_tags=args.negative_tags,
        make_instrumental=args.instrumental,
        description=args.description
    )
    
    if result:
        logger.info(f"Successfully created song: {result['title']} (ID: {result['id']})")
        logger.info(f"Audio URL: {result['audio_url']}")
        if 'video_url' in result and result['video_url']:
            logger.info(f"Video URL: {result['video_url']}")
        if 'image_url' in result and result['image_url']:
            logger.info(f"Image URL: {result['image_url']}")
    else:
        logger.error("Failed to create song")

if __name__ == "__main__":
    asyncio.run(main()) 