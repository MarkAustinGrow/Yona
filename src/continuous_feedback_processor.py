#!/usr/bin/env python
"""
Continuous Feedback Processor

This script runs continuously, checking the feedback table every hour for unprocessed feedback,
creating new songs based on the feedback, and marking the feedback as processed.
"""
import os
import sys
import json
import logging
import time
import schedule
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import YonaAgent
from src.music_api import MusicAPI
from src.supabase_client import SupabaseClient
from src.config.config import OPENAI_KEY, OPENAI_MODEL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("feedback_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    
    The song may have been created using one of two APIs:
    1. Sonic API - Uses parameters like style, negative_tags, make_instrumental, mv, gpt_description_prompt
    2. Nuro API - Uses parameters like gender, genre, mood, timbre, duration
    
    If the original parameters include 'api_used' with value 'nuro', make sure to include and modify
    the Nuro-specific parameters (gender, genre, mood, timbre). If 'api_used' is 'sonic' or not specified,
    focus on the Sonic API parameters.
    
    IMPORTANT: For the 'mv' field in Sonic API, you MUST only use one of these valid values: 'sonic-v3-5' or 'sonic-v4'.
    Any other value will cause an error. If you're unsure, use 'sonic-v4'.
    
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
    
    # Validate and fix the mv field if needed
    valid_mv_values = ['sonic-v3-5', 'sonic-v4']
    if 'mv' in modified_params:
        if modified_params['mv'] not in valid_mv_values:
            # Default to sonic-v4 if an invalid value is provided
            original_mv = modified_params['mv']
            modified_params['mv'] = 'sonic-v4'
            warning_msg = f"Warning: Invalid mv value '{original_mv}' was changed to 'sonic-v4'"
            logger.warning(warning_msg)
            print(warning_msg)
    else:
        # If mv field is missing, add it with default value
        modified_params['mv'] = 'sonic-v4'
        warning_msg = "Warning: Missing mv field was added with default value 'sonic-v4'"
        logger.warning(warning_msg)
        print(warning_msg)
    
    return modified_params

def process_feedback(feedback, agent, music_api, supabase_client):
    """
    Process a single feedback record.
    
    Args:
        feedback: Feedback record
        agent: YonaAgent instance
        music_api: MusicAPI instance
        supabase_client: SupabaseClient instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        feedback_id = feedback['id']
        song_id = feedback['song_id']
        comments = feedback['comments']
        
        logger.info(f"Processing feedback {feedback_id} for song {song_id}")
        logger.info(f"Feedback comments: {comments}")
        print(f"Processing feedback ID: {feedback_id} for song ID: {song_id}")
        
        # Get the original song
        original_song = supabase_client.get_song_by_id(song_id)
        if not original_song:
            logger.error(f"Song with ID {song_id} not found")
            return False
        
        logger.info(f"Retrieved original song: {original_song.get('title')}")
        
        # Extract the original parameters
        logger.info(f"Original song data: {json.dumps({k: v for k, v in original_song.items() if k != 'lyrics'}, indent=2, default=str)}")
        original_params = original_song.get('params_used')
        
        if not original_params:
            logger.error("Original song does not have params_used field")
            print("ERROR: Original song does not have params_used field")
            
            # Try to create default parameters from the song data
            logger.info("Attempting to create default parameters from song data")
            original_params = {
                'prompt': original_song.get('lyrics', ''),
                'title': original_song.get('title', ''),
                'style': original_song.get('style', ''),
                'negative_tags': original_song.get('negative_tags', ''),
                'make_instrumental': original_song.get('make_instrumental', False),
                'mv': original_song.get('mv', 'sonic-v4'),
                'gpt_description_prompt': original_song.get('gpt_description', ''),
                'voice_gender': 'female'
            }
            logger.info(f"Created default parameters: {json.dumps(original_params, indent=2)}")
            print("Created default parameters from song data")
        else:
            logger.info(f"Original params found: {type(original_params)}")
            
            # If original_params is a string (JSON), parse it
            if isinstance(original_params, str):
                try:
                    logger.info(f"Parsing original_params string: {original_params[:100]}...")
                    original_params = json.loads(original_params)
                    logger.info("Successfully parsed original_params JSON string")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse params_used as JSON: {str(e)}")
                    print(f"ERROR: Failed to parse params_used as JSON: {str(e)}")
                    return False
        
        # Modify parameters based on feedback
        logger.info("Modifying parameters based on feedback")
        modified_params = modify_parameters_with_openai(
            original_params, 
            comments,
            agent.openai_client
        )
        
        logger.info(f"Modified parameters: {json.dumps(modified_params, indent=2)}")
        
        # Determine which API to use based on modified parameters
        api_used = modified_params.get('api_used', 'sonic')
        is_nuro_api = False
        
        # Create a new song with the modified parameters
        logger.info(f"Creating new song with modified parameters using {api_used.upper()} API")
        
        if api_used == 'nuro':
            # Use Nuro API directly if specified in parameters
            is_nuro_api = True
            result = music_api.create_song_nuro(
                lyrics=modified_params.get('prompt', original_song.get('lyrics')),
                gender=modified_params.get('gender', 'Female'),
                genre=modified_params.get('genre', 'Pop'),
                mood=modified_params.get('mood', 'Happy'),
                timbre=modified_params.get('timbre'),
                duration=modified_params.get('duration')
            )
        else:
            # Try Sonic API first
            logger.info("Creating new song with modified parameters using SONIC API")
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
            # Check if Sonic API is under maintenance
            if isinstance(result.get('error'), str) and 'maintenance' in result.get('error'):
                logger.warning("Sonic API is under maintenance. Falling back to Nuro API.")
                
                # Map Sonic parameters to Nuro parameters
                gender = 'Female'  # Default to female voice
                if modified_params.get('voice_gender') == 'male':
                    gender = 'Male'
                
                # Extract genre and mood from style if possible
                style = modified_params.get('style', '')
                genre = 'Pop'  # Default genre
                mood = 'Happy'  # Default mood
                
                # Simple mapping of common styles to genre/mood
                if 'rock' in style.lower():
                    genre = 'Rock'
                elif 'pop' in style.lower():
                    genre = 'Pop'
                elif 'folk' in style.lower():
                    genre = 'Folk'
                
                if 'happy' in style.lower() or 'upbeat' in style.lower():
                    mood = 'Happy'
                elif 'sad' in style.lower() or 'melancholic' in style.lower():
                    mood = 'Sad'
                elif 'energetic' in style.lower():
                    mood = 'Energetic'
                
                # Try using Nuro API instead
                is_nuro_api = True
                result = music_api.create_song_nuro(
                    lyrics=modified_params.get('prompt', original_song.get('lyrics')),
                    gender=gender,
                    genre=genre,
                    mood=mood,
                    timbre=None,  # No direct mapping
                    duration=None  # Use default duration
                )
                
                # Update modified_params to reflect the API change
                modified_params['api_used'] = 'nuro'
                modified_params['gender'] = gender
                modified_params['genre'] = genre
                modified_params['mood'] = mood
                
                logger.info(f"Fallback to Nuro API with parameters: gender={gender}, genre={genre}, mood={mood}")
                
                # Check if the fallback also failed
                if result.get('status') == 'failed':
                    logger.error(f"Failed to create song with Nuro API fallback: {result.get('error')}")
                    return False
            else:
                logger.error(f"Failed to create song: {result.get('error')}")
                return False
            
        # Update is_nuro_api based on the result
        if result.get('api_used') == 'nuro':
            is_nuro_api = True
            
        logger.info(f"Song creation initiated: {result}")
        
        # Check song status until it's completed or failed
        task_id = result.get('task_id')
        if not task_id:
            logger.error("Failed to get task ID for song creation")
            return False
        
        # Poll for song status
        logger.info(f"Checking status for task: {task_id}")
        status = "pending"
        attempt = 1
        max_attempts = 60
        check_interval = 30
        song_data = None
        
        while status != "succeeded" and status != "failed" and attempt <= max_attempts:
            logger.info(f"Checking song status (attempt {attempt}/{max_attempts})...")
            
            # Use the appropriate status checking method based on the API
            if is_nuro_api:
                status_response = music_api.check_song_status_nuro(task_id)
                
                # Handle Nuro API response format
                if status_response:
                    song_data = status_response
                    # Check both 'state' and 'status' fields (Nuro API uses 'status')
                    status = song_data.get('state', song_data.get('status', 'unknown'))
                    
                    # If we have audio_url but status is still pending, we can proceed
                    if status == "pending" and song_data.get('audio_url') and song_data.get('audio_url').startswith('https://'):
                        logger.info("Song has audio URL but status is still pending. Proceeding anyway.")
                        status = "succeeded"
                    
                    # If progress is 100%, consider it succeeded regardless of status
                    if song_data.get('progress') == 100:
                        logger.info("Song progress is 100%, considering it successful.")
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
            
            # Extract data from the response
            audio_url = song_data.get('audio_url', '')
            video_url = song_data.get('video_url', '')
            image_url = song_data.get('image_url', '')
            duration = song_data.get('duration', 0)
            
            logger.info(f"Audio URL: {audio_url}")
            
            # Store the song data in Supabase
            try:
                # Get description and ensure it's not None before slicing
                description = modified_params.get('gpt_description_prompt')
                description = (description or '')[:199]  # Slice to 199 chars max
                
                # Determine which API was used
                api_used = modified_params.get('api_used', 'sonic')
                
                # Prepare song data for database
                song_data_for_db = {
                    'title': modified_params.get('title', original_song.get('title')),
                    'lyrics': modified_params.get('prompt', original_song.get('lyrics')),
                    'style': modified_params.get('style', original_song.get('style')),
                    'audio_url': audio_url,
                    'video_url': video_url,
                    'image_url': image_url,
                    'make_instrumental': modified_params.get('make_instrumental', False),
                    'mv': modified_params.get('mv', 'sonic-v4'),
                    'gpt_description': description,
                    'negative_tags': modified_params.get('negative_tags'),
                    'duration': duration,
                    'original_song_id': song_id,
                    # Removed feedback_id as it doesn't exist in the songs table
                    'persona_id': 'direct_generation',
                    'params_used': modified_params,
                    'processor_did': agent.did_manager.did if hasattr(agent, 'did_manager') else None,
                    'api_used': api_used
                }
                
                # Add Nuro-specific fields if using Nuro API
                if api_used == 'nuro':
                    song_data_for_db['gender'] = modified_params.get('gender')
                    song_data_for_db['genre'] = modified_params.get('genre')
                    song_data_for_db['mood'] = modified_params.get('mood')
                    song_data_for_db['timbre'] = modified_params.get('timbre')
                
                # Store song data in Supabase
                db_song_id = supabase_client.store_song_data(song_data_for_db)
                
                if db_song_id:
                    logger.info(f"Song data stored in Supabase: {db_song_id}")
                    logger.info(f"Successfully created song based on feedback: {modified_params.get('title', original_song.get('title'))} (ID: {db_song_id})")
                    
                    # Also store as a version in the song_versions table
                    version_data = {
                        'title': modified_params.get('title', original_song.get('title')),
                        'lyrics': modified_params.get('prompt', original_song.get('lyrics')),
                        'audio_url': audio_url,
                        'params_used': modified_params,
                        'processor_did': agent.did_manager.did if hasattr(agent, 'did_manager') else None
                    }
                    
                    # Store in song_versions table
                    version_id = supabase_client.store_song_version(song_id, version_data)
                    
                    if version_id:
                        logger.info(f"Song version stored in song_versions table: {version_id}")
                    else:
                        logger.warning("Failed to store song version in song_versions table")
                else:
                    logger.warning("Failed to store song data in Supabase")
                    # Continue anyway to mark feedback as processed
                    
                # Always mark the feedback as processed, even if DB storage failed
                # This prevents the system from getting stuck in a loop trying to process the same feedback
                if supabase_client.update_feedback(feedback_id, {"rating": 5}):
                    logger.info(f"Feedback {feedback_id} marked as processed (rating set to 5)")
                    # Return true if either the song was stored or at least the feedback was marked
                    return True
                else:
                    logger.warning(f"Failed to mark feedback {feedback_id} as processed")
                    return False
                    
            except Exception as e:
                logger.error(f"Error storing song data: {str(e)}")
                logger.exception("Exception details:")
                
                # Try to mark the feedback as processed even if storage failed
                try:
                    if supabase_client.update_feedback(feedback_id, {"rating": 5}):
                        logger.info(f"Feedback {feedback_id} marked as processed despite storage error")
                        # We still return False because the main operation (storing) failed
                    else:
                        logger.warning(f"Failed to mark feedback {feedback_id} as processed")
                except Exception as mark_error:
                    logger.error(f"Error marking feedback as processed: {str(mark_error)}")
                
                return False
            
        else:
            logger.error(f"Song creation failed with status: {status}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        logger.exception("Exception details:")
        return False

def main():
    """Main function to continuously process feedback."""
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting continuous feedback processor")
    print("Starting continuous feedback processor...")
    print("Press Ctrl+C to stop")
    
    # Initialize clients
    supabase_client = SupabaseClient()
    agent = YonaAgent(did_domain="yona.ai")
    music_api = MusicAPI()
    
    # Share DID manager with MusicAPI for authentication
    music_api.did_manager = agent.did_manager
    
    # Add Supabase log handler
    try:
        from src.logging_utils import SupabaseLogHandler
        supabase_handler = SupabaseLogHandler(supabase_client, container="feedback-processor")
        supabase_handler.setLevel(logging.INFO)  # Only log INFO and above
        supabase_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Add to the current logger
        logger.addHandler(supabase_handler)
        
        # Also add to the root logger to capture all logs
        root_logger = logging.getLogger()
        root_logger.addHandler(supabase_handler)
        
        logger.info("Supabase log handler initialized for all loggers")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase log handler: {str(e)}")
    
    # Define the log cleanup task
    def log_cleanup_task():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{current_time}] Running scheduled log cleanup")
        try:
            deleted = agent.cleanup_old_logs(days_to_keep=7)  # Keep logs for 7 days
            logger.info(f"[{current_time}] Scheduled log cleanup complete - deleted {deleted} old logs")
        except Exception as e:
            logger.error(f"[{current_time}] Error in scheduled log cleanup: {str(e)}")

    # Schedule the task to run once per day
    schedule.every(1).day.at("00:00").do(log_cleanup_task)
    
    # Set the interval (in seconds)
    interval = 3600  # 1 hour
    
    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Running feedback processing cycle at {current_time}")
            print(f"\nRunning feedback processing cycle at {current_time}")
            
            # Get only the first unprocessed feedback (limit to 1 per hour)
            try:
                # First, check if there are any unprocessed feedback records
                check_response = supabase_client.client.table("feedback").select("count").is_("rating", "null").execute()
                total_count = check_response.data[0]['count'] if check_response.data else 0
                
                if total_count == 0:
                    logger.info("No unprocessed feedback to process")
                    print("No unprocessed feedback to process")
                else:
                    logger.info(f"Found {total_count} total unprocessed feedback records")
                    print(f"Found {total_count} total unprocessed feedback records")
                    
                    # Get just the first one
                    response = supabase_client.client.table("feedback").select("*").is_("rating", "null").limit(1).execute()
                    
                    if response.data and len(response.data) > 0:
                        feedback = response.data[0]
                        logger.info(f"Processing 1 feedback record (ID: {feedback.get('id')})")
                        print(f"Processing feedback for song {feedback.get('song_id')}: {feedback.get('comments')}")
                        
                        # Add extra debug logging
                        logger.info(f"Feedback details: {json.dumps(feedback, indent=2, default=str)}")
                        
                        # Process the feedback
                        if process_feedback(feedback, agent, music_api, supabase_client):
                            logger.info("Successfully processed feedback")
                            print("Successfully processed feedback")
                        else:
                            logger.error("Failed to process feedback")
                            print("Failed to process feedback")
                    else:
                        logger.warning("Failed to retrieve the first unprocessed feedback record")
                        print("Failed to retrieve the first unprocessed feedback record")
            except Exception as e:
                logger.error(f"Error retrieving or processing feedback: {str(e)}")
                logger.exception("Exception details:")
                print(f"Error retrieving or processing feedback: {str(e)}")
            
            next_run_time = datetime.fromtimestamp(time.time() + interval).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Next processing cycle will run at {next_run_time}")
            print(f"Next processing cycle will run at {next_run_time}")
            
            # Run any pending scheduled tasks
            schedule.run_pending()
            
            # Sleep for the specified interval
            print(f"Sleeping for {interval} seconds (1 hour)...")
            print("(Press Ctrl+C to stop)")
            
            # Sleep in smaller increments to allow for more responsive Ctrl+C handling
            sleep_increment = 10  # seconds
            for _ in range(interval // sleep_increment):
                time.sleep(sleep_increment)
                # Run any pending scheduled tasks
                schedule.run_pending()
                # Check for keyboard interrupt
                if sys.stdin.isatty() and sys.stdin.readable() and sys.stdin.seekable():
                    try:
                        # Check if there's input available
                        import select
                        if select.select([sys.stdin], [], [], 0)[0]:
                            # Read a character
                            char = sys.stdin.read(1)
                            if char == 'q':
                                print("Quitting by user request...")
                                return 0
                    except:
                        pass
            
            # Sleep any remaining time
            time.sleep(interval % sleep_increment)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.exception("Exception details:")
        print(f"\nUnexpected error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
