#!/usr/bin/env python
"""
Create a song based on feedback for an existing song.

This script retrieves an existing song and its feedback, then uses OpenAI
to modify the song parameters based on the feedback, and creates a new song.
"""
import os
import sys
import json
import logging
import argparse
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import YonaAgent
from src.music_api import MusicAPI
from src.supabase_client import SupabaseClient
from src.config.config import OPENAI_KEY, OPENAI_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create a song based on feedback')
    parser.add_argument('--song-id', required=True, help='ID of the original song')
    parser.add_argument('--feedback-id', required=True, help='ID of the feedback')
    return parser.parse_args()

def modify_parameters_with_openai(original_params, feedback_comment, openai_client):
    """
    Use OpenAI to modify song parameters based on feedback.
    
    Args:
        original_params: Original parameters used to create the song
        feedback_comment: Feedback comment to incorporate
        openai_client: OpenAI client
        
    Returns:
        Modified parameters
    """
    # Create a system message for OpenAI
    system_message = """
    You are a music production assistant. You will be given the original parameters 
    used to create a song, along with feedback about the song. Your task is to modify 
    the parameters to address the feedback while keeping the core identity of the song.
    
    Return a JSON object with the modified parameters. Include all original parameters 
    with appropriate modifications based on the feedback.
    """
    
    # Create a user message with the original parameters and feedback
    user_message = f"""
    Original parameters:
    {json.dumps(original_params, indent=2)}
    
    Feedback:
    {feedback_comment}
    
    Please modify the parameters to address this feedback.
    """
    
    # Call OpenAI API
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    
    # Parse the response
    modified_params = json.loads(response.choices[0].message.content)
    
    return modified_params

def main():
    """Main function to create a song based on feedback."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    # Initialize clients
    supabase_client = SupabaseClient()
    agent = YonaAgent()
    music_api = MusicAPI()
    
    try:
        # Get the original song
        original_song = supabase_client.get_song_by_id(args.song_id)
        if not original_song:
            logger.error(f"Song with ID {args.song_id} not found")
            return 1
        
        logger.info(f"Retrieved original song: {original_song.get('title')}")
        
        # Get the feedback
        feedback = supabase_client.get_feedback_by_id(args.feedback_id)
        if not feedback:
            logger.error(f"Feedback with ID {args.feedback_id} not found")
            return 1
        
        logger.info(f"Retrieved feedback: {feedback.get('comments')}")
        
        # Extract the original parameters
        original_params = original_song.get('params_used')
        if not original_params:
            logger.error("Original song does not have params_used field")
            return 1
        
        # If original_params is a string (JSON), parse it
        if isinstance(original_params, str):
            try:
                original_params = json.loads(original_params)
            except json.JSONDecodeError:
                logger.error("Failed to parse params_used as JSON")
                return 1
        
        # Modify parameters based on feedback
        logger.info("Modifying parameters based on feedback")
        modified_params = modify_parameters_with_openai(
            original_params, 
            feedback['comments'],
            agent.openai_client
        )
        
        logger.info(f"Modified parameters: {json.dumps(modified_params, indent=2)}")
        
        # Create a new song with the modified parameters
        logger.info("Creating new song with modified parameters")
        result = music_api.create_song(
            prompt=modified_params.get('prompt', original_song.get('lyrics')),
            title=modified_params.get('title', original_song.get('title')),
            style=modified_params.get('style', original_song.get('style')),
            negative_tags=modified_params.get('negative_tags'),
            make_instrumental=modified_params.get('make_instrumental', False),
            mv=modified_params.get('mv', 'sonic-v4'),
            gpt_description_prompt=modified_params.get('gpt_description_prompt'),
            voice_gender='female'  # Hard-coded as female
        )
        
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
        max_attempts = 60
        check_interval = 30
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
                import time
                time.sleep(check_interval)  # Wait between checks
        
        if status == "succeeded" or (status == "pending" and song_data and song_data.get('audio_url')):
            logger.info(f"Song status: {status}")
            
            # Extract data from the response
            audio_url = song_data.get('audio_url', '')
            video_url = song_data.get('video_url', '')
            image_url = song_data.get('image_url', '')
            duration = song_data.get('duration', 0)
            
            logger.info(f"Audio URL: {audio_url}")
            
            # Store the song data in Supabase
            song_data_for_db = {
                'title': modified_params.get('title', original_song.get('title')),
                'lyrics': modified_params.get('prompt', original_song.get('lyrics')),
                'style': modified_params.get('style', original_song.get('style')),
                'audio_url': audio_url,
                'video_url': video_url,
                'image_url': image_url,
                'make_instrumental': modified_params.get('make_instrumental', False),
                'mv': modified_params.get('mv', 'sonic-v4'),
                'gpt_description': modified_params.get('gpt_description_prompt', '')[:199],
                'negative_tags': modified_params.get('negative_tags'),
                'duration': duration,
                'original_song_id': args.song_id,
                'feedback_id': args.feedback_id,
                'persona_id': 'direct_generation',
                'params_used': modified_params,
                'processor_did': agent.did_manager.did if hasattr(agent, 'did_manager') else None
            }
            
            # Store song data in Supabase
            db_song_id = supabase_client.store_song_data(song_data_for_db)
            
            if db_song_id:
                logger.info(f"Song data stored in Supabase: {db_song_id}")
                logger.info(f"Successfully created song based on feedback: {modified_params.get('title', original_song.get('title'))} (ID: {db_song_id})")
                logger.info(f"Audio URL: {audio_url}")
                logger.info(f"Video URL: {video_url}")
                logger.info(f"Image URL: {image_url}")
                
                # Also store as a version in the song_versions table
                version_data = {
                    'title': modified_params.get('title', original_song.get('title')),
                    'lyrics': modified_params.get('prompt', original_song.get('lyrics')),
                    'audio_url': audio_url,
                    'params_used': modified_params,
                    'processor_did': agent.did_manager.did if hasattr(agent, 'did_manager') else None
                }
                
                # Store in song_versions table
                version_id = supabase_client.store_song_version(args.song_id, version_data)
                
                if version_id:
                    logger.info(f"Song version stored in song_versions table: {version_id}")
                else:
                    logger.warning("Failed to store song version in song_versions table")
                
                # Mark the feedback as processed using 5 as a rating value
                if supabase_client.update_feedback(args.feedback_id, {"rating": 5}):
                    logger.info(f"Feedback {args.feedback_id} marked as processed (rating set to 5)")
                else:
                    logger.warning(f"Failed to mark feedback {args.feedback_id} as processed")
                
                print(f"\nCreated new song based on feedback:")
                print(f"Title: {modified_params.get('title', original_song.get('title'))}")
                print(f"ID: {db_song_id}")
                print(f"Audio URL: {audio_url}")
                if video_url:
                    print(f"Video URL: {video_url}")
                
                return 0
            else:
                logger.warning("Failed to store song data in Supabase")
                return 1
            
        else:
            logger.error(f"Song creation failed with status: {status}")
            if song_data and 'error' in song_data:
                logger.error(f"Error details: {song_data['error']}")
            else:
                logger.error("Song creation timed out or failed without error details")
            
            return 1
            
    except Exception as e:
        logger.error(f"Error creating song from feedback: {str(e)}")
        logger.exception("Exception details:")
        return 1

if __name__ == "__main__":
    sys.exit(main())
