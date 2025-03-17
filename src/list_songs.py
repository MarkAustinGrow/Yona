"""
Script to list all songs stored in the Supabase database.
"""
import os
import json
import asyncio
import argparse
from dotenv import load_dotenv
from supabase import create_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def list_songs(show_params=False, show_details=False):
    """
    List all songs from the Supabase database.
    
    Args:
        show_params (bool): Whether to show all parameters for the most recent song
        show_details (bool): Whether to show detailed information for all songs
    """
    logger.info("Listing songs from Supabase database...")
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials missing. Please check your .env file.")
        return
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        
        # Get all songs from the database
        response = supabase.table("songs").select("*").execute()
        
        # Check if the query was successful
        if hasattr(response, 'data'):
            songs = response.data
            logger.info(f"Found {len(songs)} songs in the database\n")
            
            # Display song information
            for i, song in enumerate(songs):
                print(f"Song {i+1}:")
                print(f"  ID: {song.get('id')}")
                print(f"  Title: {song.get('title')}")
                print(f"  Audio URL: {song.get('audio_url')}")
                print(f"  Created at: {song.get('created_at')}")
                
                # Display the first few lines of lyrics
                lyrics = song.get('lyrics', '')
                if lyrics:
                    lines = lyrics.split('\n')[:3]
                    print(f"  Lyrics (first 3 lines):")
                    for line in lines:
                        print(f"    {line}")
                
                # Display dedicated columns
                if song.get('duration'):
                    print(f"  Duration: {song.get('duration')} seconds")
                
                if song.get('video_url'):
                    print(f"  Video URL: {song.get('video_url')}")
                    
                if song.get('image_url'):
                    print(f"  Image URL: {song.get('image_url')}")
                
                # Display additional details if requested
                if show_details or (i == len(songs) - 1):  # Always show details for the most recent song
                    print(f"  Style: {song.get('style', 'N/A')}")
                    print(f"  Music Model: {song.get('mv', 'N/A')}")
                    
                    if song.get('make_instrumental'):
                        print(f"  Instrumental: Yes")
                    
                    if song.get('gpt_description'):
                        print(f"  Description: {song.get('gpt_description')}")
                
                # Show all parameters if requested (for backward compatibility)
                if show_params and i == len(songs) - 1:  # Only for the most recent song
                    params = song.get('params_used')
                    if params:
                        try:
                            if isinstance(params, str):
                                params_dict = json.loads(params)
                            else:
                                params_dict = params
                                
                            print("\nAll parameters used for the most recent song:")
                            for key, value in params_dict.items():
                                if key not in ['prompt', 'lyrics']:  # Skip long text fields
                                    print(f"  {key}: {value}")
                        except Exception as e:
                            logger.error(f"Error parsing params_used: {str(e)}")
                
                print()
        else:
            logger.error(f"Error listing songs: {response.error}")
            
    except Exception as e:
        logger.error(f"Exception during song listing: {str(e)}")

async def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='List all songs stored in the Supabase database')
    parser.add_argument('--show-params', action='store_true', help='Show all parameters for the most recent song')
    parser.add_argument('--show-details', action='store_true', help='Show detailed information for all songs')
    
    args = parser.parse_args()
    
    await list_songs(args.show_params, args.show_details)

if __name__ == "__main__":
    asyncio.run(main()) 