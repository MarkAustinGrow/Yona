#!/usr/bin/env python
"""
Comprehensive test script for the Nuro API integration.

This script tests both the Sonic and Nuro APIs, including status checking,
to verify the complete song creation process works correctly.
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

def check_song_status(music_api, task_id, is_nuro=False, max_attempts=10, check_interval=30):
    """
    Check the status of a song creation task.
    
    Args:
        music_api: MusicAPI instance
        task_id: Task ID from song creation
        is_nuro: Whether this is a Nuro API task
        max_attempts: Maximum number of status check attempts
        check_interval: Time in seconds between status checks
        
    Returns:
        Tuple of (success, song_data)
    """
    status = "pending"
    attempt = 1
    song_data = None
    
    while status != "succeeded" and status != "failed" and attempt <= max_attempts:
        logger.info(f"Checking song status (attempt {attempt}/{max_attempts})...")
        
        # Use the appropriate status checking method based on the API
        if is_nuro:
            status_response = music_api.check_song_status_nuro(task_id)
            
            # Handle Nuro API response format
            if status_response:
                song_data = status_response
                status = song_data.get('state', 'unknown')
                
                # If we have audio_url but status is still pending, we can proceed
                if status == "pending" and song_data.get('audio_url') and song_data.get('audio_url').startswith('https://'):
                    logger.info("Song has audio URL but status is still pending. Proceeding anyway.")
                    status = "succeeded"
        else:
            status_response = music_api.check_song_status(task_id)
            
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
        logger.info(f"Audio URL: {audio_url}")
        
        return True, song_data
    else:
        logger.error(f"Song creation failed with status: {status}")
        if song_data and 'error' in song_data:
            logger.error(f"Error details: {song_data['error']}")
        else:
            logger.error("Song creation timed out or failed without error details")
        
        return False, song_data

def test_sonic_api():
    """Test the Sonic API for song creation and status checking."""
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
        return False, None
    
    # Check song status
    task_id = result.get('task_id')
    if not task_id:
        logger.error("Failed to get task ID for Sonic song creation")
        return False, None
    
    logger.info(f"Sonic API task ID: {task_id}")
    
    # Check status until completion or failure
    success, song_data = check_song_status(music_api, task_id, is_nuro=False)
    
    if success:
        logger.info("Sonic API test completed successfully")
        return True, song_data
    else:
        logger.error("Sonic API test failed during status checking")
        return False, song_data

def test_nuro_api():
    """Test the Nuro API for song creation and status checking."""
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
        return False, None
    
    # Check song status
    task_id = result.get('task_id')
    if not task_id:
        logger.error("Failed to get task ID for Nuro song creation")
        return False, None
    
    logger.info(f"Nuro API task ID: {task_id}")
    
    # Check status until completion or failure
    success, song_data = check_song_status(music_api, task_id, is_nuro=True)
    
    if success:
        logger.info("Nuro API test completed successfully")
        return True, song_data
    else:
        logger.error("Nuro API test failed during status checking")
        return False, song_data

def compare_results(sonic_data, nuro_data):
    """Compare the results from both APIs."""
    logger.info("Comparing results from both APIs...")
    
    if not sonic_data or not nuro_data:
        logger.warning("Cannot compare results: missing data")
        return
    
    # Compare audio URLs
    sonic_audio = sonic_data.get('audio_url', '')
    nuro_audio = nuro_data.get('audio_url', '')
    
    logger.info(f"Sonic API audio URL: {sonic_audio}")
    logger.info(f"Nuro API audio URL: {nuro_audio}")
    
    # Compare durations
    sonic_duration = sonic_data.get('duration', 0)
    nuro_duration = nuro_data.get('duration', 0)
    
    logger.info(f"Sonic API duration: {sonic_duration} seconds")
    logger.info(f"Nuro API duration: {nuro_duration} seconds")
    
    # Compare other metadata
    logger.info("Sonic API metadata:")
    for key, value in sonic_data.items():
        if key not in ['audio_url', 'duration']:
            logger.info(f"  {key}: {value}")
    
    logger.info("Nuro API metadata:")
    for key, value in nuro_data.items():
        if key not in ['audio_url', 'duration']:
            logger.info(f"  {key}: {value}")

def main():
    """Main function to run the tests."""
    # Load environment variables
    load_dotenv()
    
    # Test Sonic API
    logger.info("=== TESTING SONIC API ===")
    sonic_success, sonic_data = test_sonic_api()
    logger.info(f"Sonic API test {'passed' if sonic_success else 'failed'}")
    
    # Wait a bit before testing the Nuro API
    time.sleep(2)
    
    # Test Nuro API
    logger.info("=== TESTING NURO API ===")
    nuro_success, nuro_data = test_nuro_api()
    logger.info(f"Nuro API test {'passed' if nuro_success else 'failed'}")
    
    # Compare results if both tests passed
    if sonic_success and nuro_success:
        logger.info("=== COMPARING RESULTS ===")
        compare_results(sonic_data, nuro_data)
    
    # Overall result
    if sonic_success and nuro_success:
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
