"""
Advanced Song Creation Example

This script demonstrates how to use all available parameters from Suno/MusicAPI.ai
to create a highly customized song.

Available parameters:
- custom_mode: boolean (required) - If you want to customize the lyrics, this should be true
- prompt: string (required) - Song lyrics, should be less than 3000 characters
- title: string (optional) - Song title, should be less than 80 characters
- tags/style: string (optional) - Song tags/style, should be less than 200 characters
- negative_tags: string (optional) - Elements you want to avoid in your songs
- mv: string (required) - Music model, which can be sonic-v3-5 or sonic-v4
- make_instrumental: boolean (optional) - Instrumental version
- gpt_description_prompt: string (optional) - Description of the music
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from music_api import MusicAPI
from supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def create_advanced_song():
    """Create a song with all available parameters."""
    # Initialize API clients
    music_api = MusicAPI(simulation_mode=False)
    supabase = SupabaseClient(simulation_mode=False)
    
    # Define song parameters
    title = "Neon Dreams"
    
    # Define song lyrics with proper structure
    lyrics = """
    [Verse 1]
    Digital lights paint the sky tonight
    Your pixels shine in the virtual night
    We're dancing through the data stream
    Creating memories in this digital dream
    
    [Pre-Chorus]
    One click, two click, moving closer
    Heart sync, can't stop, feeling stronger
    
    [Chorus]
    Neon dreams illuminate our way
    Electric love flowing through the day
    This moment is ours to own
    In this digital world, we're never alone
    
    [Verse 2]
    Cyber signs light up the way
    Your voice echoes in my neural space
    We're running through the server streets
    Leaving worries in deleted files
    
    [Bridge]
    Time freezes when we're connected
    Nothing else matters, just this feeling selected
    
    [Chorus]
    Neon dreams illuminate our way
    Electric love flowing through the day
    This moment is ours to own
    In this digital world, we're never alone
    """
    
    # Define style/tags - can include multiple genres separated by commas
    style = "kpop, electronic, synthwave, future pop"
    
    # Define elements to avoid in the song
    negative_tags = "sad, slow, ballad, acoustic"
    
    # Choose the music model
    mv = "sonic-v4"  # Latest model for best quality
    
    # Whether to create an instrumental version
    make_instrumental = False
    
    # Detailed description for the GPT model to better understand the desired style
    description = """
    An energetic K-pop song with strong synthwave and electronic influences. 
    The song should feature bright synths, a driving beat, and a futuristic atmosphere.
    The vocals should be clear and powerful, with a catchy chorus that has an anthemic quality.
    The production should be polished with modern electronic elements, including:
    - Punchy electronic drums
    - Arpeggiated synths
    - Bright pad sounds
    - A strong bass line
    The song should have a positive, uplifting feel with a tempo around 120-130 BPM.
    """
    
    # Create the song with all parameters
    logger.info(f"Creating advanced song: {title}")
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
                
                # Continue polling if we get a pending or running status
                if status_result.get("status") in ["pending", "running"]:
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
                    
                    if status_result.get("video_url"):
                        logger.info(f"Video URL: {status_result.get('video_url')}")
                    
                    if status_result.get("image_url"):
                        logger.info(f"Image URL: {status_result.get('image_url')}")
                    
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
                    
                    supabase_result = await supabase.store_song_data(
                        title=title,
                        persona_id="direct_generation",  # No persona used
                        lyrics=status_result.get("lyrics", lyrics),
                        audio_url=status_result.get("audio_url", ""),
                        params_used=params_used
                    )
                    
                    if supabase_result:
                        logger.info(f"Song data stored in Supabase: {supabase_result}")
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
    """Main function to run the example."""
    result = await create_advanced_song()
    
    if result:
        logger.info("Advanced song creation example completed successfully!")
        logger.info(f"Song ID: {result.get('id')}")
        logger.info(f"Title: {result.get('title')}")
        logger.info(f"Audio URL: {result.get('audio_url')}")
    else:
        logger.error("Advanced song creation example failed")

if __name__ == "__main__":
    asyncio.run(main()) 