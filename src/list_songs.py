"""
Script to list all songs in the Supabase database.
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def list_songs():
    """List all songs in the Supabase database."""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials missing. Please check your .env file.")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        
        # Query all songs
        response = supabase.table("songs").select("*").execute()
        
        if hasattr(response, 'data'):
            songs = response.data
            logger.info(f"Found {len(songs)} songs in the database")
            
            # Print song details
            for i, song in enumerate(songs, 1):
                print(f"\nSong {i}:")
                print(f"  ID: {song.get('id')}")
                print(f"  Title: {song.get('title')}")
                print(f"  Audio URL: {song.get('audio_url')}")
                print(f"  Created at: {song.get('created_at')}")
                
                # Print lyrics (first few lines)
                if 'lyrics' in song and song['lyrics']:
                    lyrics_lines = song['lyrics'].split('\n')
                    print(f"  Lyrics (first 3 lines): ")
                    for j in range(min(3, len(lyrics_lines))):
                        if lyrics_lines[j].strip():
                            print(f"    {lyrics_lines[j].strip()}")
                
                # Extract additional details from params_used if available
                if 'params_used' in song and song['params_used']:
                    try:
                        import json
                        params = json.loads(song['params_used']) if isinstance(song['params_used'], str) else song['params_used']
                        if 'duration' in params:
                            print(f"  Duration: {params.get('duration')} seconds")
                        if 'video_url' in params:
                            print(f"  Video URL: {params.get('video_url')}")
                        if 'image_url' in params:
                            print(f"  Image URL: {params.get('image_url')}")
                    except Exception as e:
                        logger.error(f"Error parsing params_used: {str(e)}")
                        print(f"  Raw params_used: {song['params_used'][:100]}...")
            
            return True
        else:
            logger.error("No data returned from Supabase")
            return False
        
    except Exception as e:
        logger.error(f"Error listing songs: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Listing songs from Supabase database...")
    list_songs() 