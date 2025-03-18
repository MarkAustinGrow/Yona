#!/usr/bin/env python
"""
List Songs Script for Yona

This script lists songs stored in the Supabase database.
"""
import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='List songs stored in the database')
    
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of songs to list')
    parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    parser.add_argument('--id', help='Specific song ID to retrieve')
    parser.add_argument('--show-params', action='store_true', help='Show full song parameters')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--simulation', action='store_true', help='Run in simulation mode')
    
    return parser.parse_args()

def display_song(song: Dict[str, Any], show_params: bool = False, json_output: bool = False):
    """
    Display information about a song.
    
    Args:
        song: Dictionary containing song data
        show_params: Whether to show full song parameters
        json_output: Whether to output in JSON format
    """
    if json_output:
        # Print the entire song data as JSON
        print(json.dumps(song, indent=2))
        return
    
    # Print basic song information
    print(f"ID: {song.get('id', 'Unknown')}")
    print(f"Title: {song.get('title', 'Unknown')}")
    print(f"Audio URL: {song.get('audio_url', 'None')}")
    
    # Print additional information if requested
    if show_params:
        print(f"Style: {song.get('style', 'None')}")
        print(f"Created At: {song.get('created_at', 'Unknown')}")
        print(f"Duration: {song.get('duration', 0)} seconds")
        print(f"Video URL: {song.get('video_url', 'None')}")
        print(f"Image URL: {song.get('image_url', 'None')}")
        
        # Print lyrics (first 3 lines)
        lyrics = song.get('lyrics', '')
        if lyrics:
            lyrics_lines = lyrics.split('\n')
            print(f"Lyrics (first 3 lines):")
            for i in range(min(3, len(lyrics_lines))):
                print(f"  {lyrics_lines[i]}")
            if len(lyrics_lines) > 3:
                print(f"  ... ({len(lyrics_lines) - 3} more lines)")
        
        # Print other fields
        print(f"Make Instrumental: {song.get('make_instrumental', False)}")
        print(f"MV Type: {song.get('mv', 'None')}")
        print(f"Negative Tags: {song.get('negative_tags', 'None')}")
        print(f"Clip ID: {song.get('clip_id', 'None')}")
        
        # Print original prompt if available
        if 'original_prompt' in song:
            print(f"Original Prompt: {song.get('original_prompt')}")
        
        # Print song concept if available
        if 'song_concept' in song:
            try:
                concept = json.loads(song.get('song_concept', '{}'))
                print("Song Concept:")
                for key, value in concept.items():
                    print(f"  {key}: {value}")
            except:
                print(f"Song Concept: {song.get('song_concept', 'None')}")

def main():
    """Main function to list songs."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    # Initialize Supabase client
    supabase_client = SupabaseClient(simulation_mode=args.simulation)
    
    try:
        if args.id:
            # Retrieve a specific song
            logger.info(f"Retrieving song with ID: {args.id}")
            song = supabase_client.get_song_by_id(args.id)
            
            if song:
                display_song(song, args.show_params, args.json)
            else:
                logger.error(f"No song found with ID: {args.id}")
                return 1
        else:
            # List songs
            logger.info(f"Listing songs (limit: {args.limit}, offset: {args.offset})")
            songs = supabase_client.list_songs(args.limit, args.offset)
            
            if not songs:
                logger.warning("No songs found")
                return 0
            
            if args.json:
                # Print all songs as JSON
                print(json.dumps(songs, indent=2))
            else:
                # Print each song
                for i, song in enumerate(songs):
                    if i > 0:
                        print("\n" + "-" * 50 + "\n")
                    display_song(song, args.show_params, False)
            
        return 0
        
    except Exception as e:
        logger.error(f"Error listing songs: {str(e)}")
        logger.exception("Exception details:")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 