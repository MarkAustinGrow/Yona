#!/usr/bin/env python
"""
Test script for the Nuro API integration.

This script tests both the Sonic and Nuro APIs to verify they're working correctly.
"""
import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.music_api import MusicAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sonic_api():
    """Test the Sonic API for song creation."""
    logger.info("Testing Sonic API...")
    
    # Initialize MusicAPI
    music_api = MusicAPI()
    
    # Sample lyrics
    lyrics = """
    [Verse 1]
    Walking through the city lights
    Memories flashing in my mind
    Every corner holds a story
    Of the times we left behind

    [Chorus]
    But I'm moving forward now
    No looking back, I've made a vow
    The future's bright, I'll find my way
    A brand new chapter starts today
    """
    
    # Create a song using the Sonic API
    result = music_api.create_song(
        prompt=lyrics,
        title="Moving Forward",
        style="pop, upbeat",
        voice_gender="female"
    )
    
    logger.info(f"Sonic API result: {result}")
    
    if result.get('status') == 'failed':
        logger.error(f"Sonic API test failed: {result.get('error')}")
        return False
    
    # Check song status
    task_id = result.get('task_id')
    if not task_id:
        logger.error("Failed to get task ID for Sonic song creation")
        return False
    
    logger.info(f"Sonic API task ID: {task_id}")
    logger.info("Sonic API test completed successfully")
    return True

def test_nuro_api():
    """Test the Nuro API for song creation."""
    logger.info("Testing Nuro API...")
    
    # Initialize MusicAPI
    music_api = MusicAPI()
    
    # Sample lyrics
    lyrics = """
    [Verse 1]
    Walking through the city lights
    Memories flashing in my mind
    Every corner holds a story
    Of the times we left behind

    [Chorus]
    But I'm moving forward now
    No looking back, I've made a vow
    The future's bright, I'll find my way
    A brand new chapter starts today
    """
    
    # Create a song using the Nuro API
    result = music_api.create_song_nuro(
        lyrics=lyrics,
        gender="Female",
        genre="Pop",
        mood="Happy",
        timbre="Bright",
        duration=120
    )
    
    logger.info(f"Nuro API result: {result}")
    
    if result.get('status') == 'failed':
        logger.error(f"Nuro API test failed: {result.get('error')}")
        return False
    
    # Check song status
    task_id = result.get('task_id')
    if not task_id:
        logger.error("Failed to get task ID for Nuro song creation")
        return False
    
    logger.info(f"Nuro API task ID: {task_id}")
    logger.info("Nuro API test completed successfully")
    return True

def main():
    """Main function to run the tests."""
    # Load environment variables
    load_dotenv()
    
    # Test both APIs
    sonic_result = test_sonic_api()
    logger.info(f"Sonic API test {'passed' if sonic_result else 'failed'}")
    
    # Wait a bit before testing the Nuro API
    time.sleep(2)
    
    nuro_result = test_nuro_api()
    logger.info(f"Nuro API test {'passed' if nuro_result else 'failed'}")
    
    # Overall result
    if sonic_result and nuro_result:
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
