"""
Script to create a song similar to a previous one by reusing parameters.
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

async def get_song_by_id(song_id):
    """Get a song from Supabase by its ID."""
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
        
        # Query the song by ID
        response = supabase.table("songs").select("*").eq("id", song_id).execute()
        
        if hasattr(response, 'data') and len(response.data) > 0:
            song = response.data[0]
            logger.info(f"Found song: {song.get('title')}")
            return song
        else:
            logger.error(f"No song found with ID: {song_id}")
            return None
        
    except Exception as e:
        logger.error(f"Error getting song: {str(e)}")
        return None

async def list_songs():
    """List all songs in the Supabase database."""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials missing. Please check your .env file.")
        return []
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        
        # Query all songs
        response = supabase.table("songs").select("*").execute()
        
        if hasattr(response, 'data'):
            songs = response.data
            logger.info(f"Found {len(songs)} songs in the database")
            return songs
        else:
            logger.error("No data returned from Supabase")
            return []
        
    except Exception as e:
        logger.error(f"Error listing songs: {str(e)}")
        return []

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

async def create_similar_song(reference_song_id, new_lyrics, new_title, modify_params=None):
    """Create a song similar to a reference song by reusing parameters."""
    # Get the reference song
    reference_song = await get_song_by_id(reference_song_id)
    if not reference_song:
        logger.error("Cannot create similar song: reference song not found")
        return None
    
    # Extract parameters from the reference song
    try:
        params_used = json.loads(reference_song['params_used']) if isinstance(reference_song['params_used'], str) else reference_song['params_used']
    except Exception as e:
        logger.error(f"Error parsing params_used: {str(e)}")
        return None
    
    # Initialize MusicAPI
    music_api = MusicAPI(simulation_mode=False)
    
    # Prepare parameters for the new song
    style = params_used.get('style', params_used.get('tags', 'kpop'))
    mv = params_used.get('mv', 'sonic-v3-5')
    negative_tags = params_used.get('negative_tags', None)
    make_instrumental = params_used.get('make_instrumental', False)
    gpt_description_prompt = params_used.get('gpt_description_prompt', None)
    
    # Apply any parameter modifications
    if modify_params:
        if 'style' in modify_params:
            style = modify_params['style']
        if 'mv' in modify_params:
            mv = modify_params['mv']
        if 'negative_tags' in modify_params:
            negative_tags = modify_params['negative_tags']
        if 'make_instrumental' in modify_params:
            make_instrumental = modify_params['make_instrumental']
        if 'gpt_description_prompt' in modify_params:
            gpt_description_prompt = modify_params['gpt_description_prompt']
    
    # Create the new song
    logger.info(f"Creating new song '{new_title}' similar to '{reference_song['title']}'")
    song_result = music_api.create_song(
        prompt=new_lyrics,
        style=style,
        title=new_title,
        mv=mv,
        negative_tags=negative_tags,
        make_instrumental=make_instrumental,
        gpt_description_prompt=gpt_description_prompt
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
                if status_result.get("status") == "pending":
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
                    new_params_used = {
                        "prompt": new_lyrics,
                        "style": style,
                        "title": new_title,
                        "mv": mv,
                        "negative_tags": negative_tags,
                        "make_instrumental": make_instrumental,
                        "gpt_description_prompt": gpt_description_prompt,
                        "reference_song_id": reference_song_id,
                        "image_url": status_result.get("image_url", ""),
                        "video_url": status_result.get("video_url", ""),
                        "duration": status_result.get("duration", 0),
                        "created_at": status_result.get("created_at", "")
                    }
                    
                    supabase_result = await store_song_data(
                        title=new_title,
                        persona_id="direct_generation",  # No persona used
                        lyrics=status_result.get("lyrics", new_lyrics),
                        audio_url=status_result.get("audio_url", ""),
                        params_used=new_params_used
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
    parser = argparse.ArgumentParser(description='Create a song similar to a previous one')
    parser.add_argument('--list', action='store_true', help='List all songs in the database')
    parser.add_argument('--reference', type=str, help='ID of the reference song')
    parser.add_argument('--title', type=str, help='Title for the new song')
    parser.add_argument('--lyrics', type=str, help='Lyrics for the new song')
    parser.add_argument('--style', type=str, help='Style/tags for the new song')
    parser.add_argument('--mv', type=str, help='Music model to use (sonic-v3-5 or sonic-v4)')
    parser.add_argument('--negative-tags', type=str, help='Elements to avoid in the song')
    parser.add_argument('--instrumental', action='store_true', help='Create an instrumental version')
    parser.add_argument('--description', type=str, help='Description of the music')
    
    args = parser.parse_args()
    
    if args.list:
        # List all songs
        songs = await list_songs()
        print("\nAvailable songs:")
        for i, song in enumerate(songs, 1):
            print(f"{i}. ID: {song.get('id')}, Title: {song.get('title')}")
        return
    
    if not args.reference or not args.title or not args.lyrics:
        logger.error("Missing required arguments: --reference, --title, and --lyrics are required")
        return
    
    # Prepare parameter modifications
    modify_params = {}
    if args.style:
        modify_params['style'] = args.style
    if args.mv:
        modify_params['mv'] = args.mv
    if args.negative_tags:
        modify_params['negative_tags'] = args.negative_tags
    if args.instrumental:
        modify_params['make_instrumental'] = True
    if args.description:
        modify_params['gpt_description_prompt'] = args.description
    
    # Create a similar song
    result = await create_similar_song(args.reference, args.lyrics, args.title, modify_params)
    
    if result:
        logger.info(f"Successfully created similar song: {result['title']} (ID: {result['id']})")
    else:
        logger.error("Failed to create similar song")

if __name__ == "__main__":
    asyncio.run(main()) 