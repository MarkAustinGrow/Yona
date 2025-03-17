"""
Main entry point for the Yona AI K-pop star system.
"""
import asyncio
import os
import time
from dotenv import load_dotenv
from agent import YonaAgent
from music_api import MusicAPI
from db import Database
from supabase_client import SupabaseClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Simulation mode flags
SIMULATE_OPENAI = True  # Set to True to simulate OpenAI calls (save costs)
SIMULATE_MUSICAPI = False  # Set to False to use the real MusicAPI.ai endpoint

async def main():
    """Main function to run the Yona AI K-pop star system."""
    logger.info("Starting Yona AI K-pop star system")
    
    # Initialize API clients
    music_api = MusicAPI(simulation_mode=SIMULATE_MUSICAPI)
    supabase = SupabaseClient(simulation_mode=False)  # Use real Supabase client
    
    # Display simulation status
    if SIMULATE_OPENAI:
        logger.info("OpenAI simulation mode: ENABLED (to save API costs)")
    if SIMULATE_MUSICAPI:
        logger.info("MusicAPI simulation mode: ENABLED (persona feature is unstable)")
    else:
        logger.info("MusicAPI using REAL API endpoint")
    logger.info("Supabase using REAL database connection")
    
    # Create a test song directly (without persona)
    logger.info("Creating a test song using real MusicAPI.ai endpoint...")
    
    # Sample lyrics for a K-pop song
    song_lyrics = """
    [Verse 1]
    Bright lights in the city tonight
    Your smile shines even brighter
    We're dancing through the moments
    Creating memories together
    
    [Pre-Chorus]
    One step, two step, moving closer
    Heart beat, can't stop, feeling stronger
    
    [Chorus]
    Shine like the stars above
    Energy flowing through us
    This moment is ours to own
    Together we're never alone
    
    [Verse 2]
    Neon signs light up the way
    Your voice echoes in my mind
    We're running through the city streets
    Leaving worries far behind
    
    [Bridge]
    Time stands still when we're together
    Nothing else matters, just this feeling forever
    
    [Chorus]
    Shine like the stars above
    Energy flowing through us
    This moment is ours to own
    Together we're never alone
    """
    
    # Create the song using the updated API format with all available parameters
    song_result = music_api.create_song(
        prompt=song_lyrics,
        style="kpop",
        title="Shine Like Stars",
        mv="sonic-v3-5",
        negative_tags="sad, melancholic, slow",
        make_instrumental=False,
        gpt_description_prompt="An energetic K-pop song with bright EDM influences, featuring catchy hooks and occasional rap segments. The song has a positive, uplifting message about friendship and enjoying life together."
    )
    
    # Log the result
    if "error" in song_result:
        logger.error(f"Error creating song: {song_result['error']}")
    else:
        logger.info(f"Song creation initiated: {song_result}")
        
        # If not in simulation mode, we need to poll for the song status
        if not SIMULATE_MUSICAPI:
            task_id = song_result.get("task_id")
            if task_id:
                logger.info(f"Checking status for task: {task_id}")
                
                # Poll for the song status (in a real app, this would be a background task)
                max_attempts = 30
                for attempt in range(max_attempts):
                    logger.info(f"Checking song status (attempt {attempt+1}/{max_attempts})...")
                    
                    # Wait before checking
                    time.sleep(30)
                    
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
                    # The status will be "pending", "running", or "succeeded" according to the API docs
                    if status_result.get("status") == "succeeded":
                        logger.info("Song creation completed successfully!")
                        logger.info(f"Audio URL: {status_result.get('audio_url')}")
                        
                        # Store song data in Supabase
                        supabase_result = await supabase.store_song_data(
                            title=status_result.get("title", "Shine Like Stars"),
                            persona_id="direct_generation",  # No persona used
                            lyrics=status_result.get("lyrics", song_lyrics),
                            audio_url=status_result.get("audio_url", ""),
                            params_used={
                                "prompt": song_lyrics,
                                "style": "kpop",
                                "title": "Shine Like Stars",
                                "mv": "sonic-v3-5",
                                "image_url": status_result.get("image_url", ""),
                                "video_url": status_result.get("video_url", ""),
                                "duration": status_result.get("duration", 0),
                                "created_at": status_result.get("created_at", "")
                            }
                        )
                        logger.info(f"Song data stored in Supabase: {supabase_result}")
                        break
                    
                    # If the song failed, log the error
                    if status_result.get("status") == "failed":
                        logger.error(f"Song creation failed: {status_result}")
                        break
        else:
            # In simulation mode, we can just store the simulated song data
            logger.info("Simulating successful song creation")
            
            # Store song data in Supabase
            supabase_result = await supabase.store_song_data(
                title="Shine Like Stars",
                persona_id="direct_generation",  # No persona used
                lyrics=song_lyrics,
                audio_url="https://example.com/simulated_song.mp3",
                params_used={
                    "prompt": song_lyrics,
                    "style": "kpop",
                    "title": "Shine Like Stars",
                    "mv": "sonic-v3-5"
                }
            )
            logger.info(f"Song data stored in Supabase: {supabase_result}")
    
    logger.info("Yona AI K-pop star system completed")

if __name__ == "__main__":
    asyncio.run(main()) 