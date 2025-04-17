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

def process_influence_music(record, agent, music_api, supabase_client):
    """
    Process a single influence_music record with OpenAI assistance.
    
    Args:
        record: Influence music record
        agent: YonaAgent instance
        music_api: MusicAPI instance
        supabase_client: SupabaseClient instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        record_id = record['id']
        url = record.get('url', '')
        analysis = record.get('analysis', {})
        
        # Extract parameters from analysis
        bpm = analysis.get('bpm')
        key = analysis.get('key')
        moods = []
        
        # Extract moods and their scores from the analysis
        if 'moods' in analysis and isinstance(analysis['moods'], list):
            for mood_obj in analysis['moods']:
                if isinstance(mood_obj, dict):
                    mood_name = mood_obj.get('name')
                    mood_score = mood_obj.get('score', 0)
                    if mood_name and mood_score >= 50:  # Only use moods with score >= 50
                        moods.append(mood_name)
        
        # Get the highest scoring mood as the primary mood
        primary_mood = moods[0] if moods else 'Energetic'  # Default to Energetic if no moods found
        
        logger.info(f"Processing influence music record {record_id}")
        logger.info(f"URL: {url}, BPM: {bpm}, Key: {key}, Moods: {moods}")
        print(f"Processing influence music record ID: {record_id}")
        
        # Create a base parameters object to send to OpenAI
        base_params = {
            'api_used': 'sonic',
            'title': "New Song",  # Generic title without URL
            'bpm': bpm,
            'key': key,
            'moods': moods,
            'make_instrumental': False,
            'mv': 'sonic-v4',
            'voice_gender': 'female'
        }
        
        # Use OpenAI to generate optimized parameters
        logger.info("Using OpenAI to generate optimized parameters for influence music")
        system_message = """
        You are a music production assistant. You will be given musical analysis data 
        from a reference track, including BPM, key, and moods. Your task is to create 
        optimal parameters for generating a new song inspired by these characteristics.
        
        Return a JSON object with the following parameters for the Sonic API:
        - title: A creative and unique title for the song summarising the lyrics in one or two words (DO NOT include any URLs in the title)
        - style: Style tags for the song (incorporate BPM, key, and moods in a format Sonic API will understand)
        - negative_tags: Tags to avoid in generation
        - make_instrumental: Boolean indicating if the song should be instrumental (usually false)
        - mv: Music video generation type (use 'sonic-v4')
        - gpt_description_prompt: A brief description to guide generation (max 199 characters)
        - voice_gender: Gender of the singer's voice (use 'female')
        
        Also include these fields for compatibility:
        - api_used: Set to 'sonic'
        - prompt: UNIQUE AND CREATIVE LYRICS that match the mood and style
        
        CRITICAL REQUIREMENTS FOR LYRICS:
        1. Create COMPLETELY UNIQUE lyrics for each song - do not use generic templates
        2. Write at least 8-12 lines of lyrics (not just 2-3 lines)
        3. Make the lyrics specific to the mood, key, and BPM of the reference track
        4. Avoid generic phrases like "La la la" or "Feel the rhythm"
        5. Include a verse and chorus structure when possible
        6. The lyrics should tell a story or convey a specific emotion
        
        IMPORTANT: For the 'style' field, format it as a comma-separated string that effectively 
        communicates the musical characteristics to the Sonic API. Don't just list BPM and key 
        directly, but incorporate them into appropriate style descriptions.
        """
        
        user_message = f"""
        Reference track analysis:
        {json.dumps(base_params, indent=2)}
        
        Additional details:
        - BPM: {bpm}
        - Key: {key}
        - Moods: {', '.join(moods) if moods else 'Unknown'}
        
        Please generate optimal parameters for creating a song inspired by these characteristics.
        """
        
        try:
            # Call OpenAI API
            response = agent.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Parse the response
            optimized_params = json.loads(response.choices[0].message.content)
            logger.info(f"OpenAI generated parameters: {json.dumps(optimized_params, indent=2)}")
            
            # Validate and fix the mv field if needed
            valid_mv_values = ['sonic-v3-5', 'sonic-v4']
            if 'mv' in optimized_params:
                if optimized_params['mv'] not in valid_mv_values:
                    original_mv = optimized_params['mv']
                    optimized_params['mv'] = 'sonic-v4'
                    logger.warning(f"Invalid mv value '{original_mv}' was changed to 'sonic-v4'")
            else:
                optimized_params['mv'] = 'sonic-v4'
                logger.warning("Missing mv field was added with default value 'sonic-v4'")
            
            # Extract key parameters for song creation
            # Use a generic title if OpenAI doesn't provide one or if the title contains a URL
            title = optimized_params.get('title', '')
            if not title or 'http' in title.lower():
                # Generate a title based on the primary mood and current timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                title = f"{primary_mood} Melody {timestamp}"
                logger.warning(f"Using generic title '{title}' because OpenAI provided an invalid or missing title")
            
            style = optimized_params.get('style', '')
            negative_tags = optimized_params.get('negative_tags')
            make_instrumental = optimized_params.get('make_instrumental', False)
            mv = optimized_params.get('mv', 'sonic-v4')
            gpt_description = optimized_params.get('gpt_description_prompt', '')
            voice_gender = optimized_params.get('voice_gender', 'female')
            
            # Use lyrics from OpenAI if provided, otherwise use default
            lyrics = optimized_params.get('prompt')
            if not lyrics:
                lyrics = "La la la, singing with the melody\nFeel the rhythm, let the music flow through me\n"
                lyrics += "Dancing to the beat, this is where I want to be\nLet your heart soar free, just follow me"
            
        except Exception as e:
            error_msg = f"Error using OpenAI to generate parameters: {str(e)}"
            logger.error(error_msg)
            logger.exception("Exception details:")
            
            # Provide detailed error information
            error_context = {
                "operation": "OpenAI parameter generation",
                "record_id": record_id,
                "url": url,
                "analysis_data": {
                    "bpm": bpm,
                    "key": key,
                    "moods": moods
                },
                "error": str(e)
            }
            
            logger.error(f"Detailed error context: {json.dumps(error_context, indent=2, default=str)}")
            
            # Instead of silently falling back, raise an exception to be handled at a higher level
            # This ensures the issue is visible and can be properly addressed
            raise RuntimeError(f"Failed to generate parameters with OpenAI: {str(e)}. See logs for details.")
        
        # Create a new song using the optimized parameters
        logger.info(f"Creating new song with optimized parameters: title={title}, style={style}")
        
        # Use create_song with the optimized parameters
        result = music_api.create_song(
            prompt=lyrics,
            title=title,
            style=style,
            negative_tags=negative_tags,
            make_instrumental=make_instrumental,
            mv=mv,
            gpt_description_prompt=gpt_description[:199] if gpt_description else None,
            voice_gender=voice_gender
        )
        
        if result.get('status') == 'failed':
            logger.error(f"Failed to create song: {result.get('error')}")
            return False
            
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
                # Store the original analysis in the optimized_params
                optimized_params['original_analysis'] = analysis
                
                # Prepare song data for database
                song_data_for_db = {
                    'title': title,
                    'lyrics': lyrics,
                    'style': style,
                    'audio_url': audio_url,
                    'video_url': video_url,
                    'image_url': image_url,
                    'make_instrumental': make_instrumental,
                    'mv': mv,
                    'gpt_description': gpt_description[:199] if gpt_description else None,
                    'negative_tags': negative_tags,
                    'duration': duration,
                    'persona_id': 'direct_generation',
                    'params_used': optimized_params,
                    'processor_did': agent.did_manager.did if hasattr(agent, 'did_manager') else None,
                    'api_used': 'sonic'
                }
                
                # Store song data in Supabase
                db_song_id = supabase_client.store_song_data(song_data_for_db)
                
                if db_song_id:
                    logger.info(f"Song data stored in Supabase: {db_song_id}")
                    logger.info(f"Successfully created song from URL: {url} (ID: {db_song_id})")
                    
                    # Mark the influence music record as processed
                    if supabase_client.mark_influence_music_processed(record_id, song_id=db_song_id):
                        logger.info(f"Influence music record {record_id} marked as processed with song_id {db_song_id}")
                        return True
                    else:
                        logger.warning(f"Failed to mark influence music record {record_id} as processed")
                        return False
                else:
                    logger.warning("Failed to store song data in Supabase")
                    return False
                    
            except Exception as e:
                logger.error(f"Error storing song data: {str(e)}")
                logger.exception("Exception details:")
                return False
            
        else:
            logger.error(f"Song creation failed with status: {status}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing influence music record: {str(e)}")
        logger.exception("Exception details:")
        return False

def check_for_unprocessed_feedback(agent, music_api, supabase_client):
    """
    Check for unprocessed feedback and process it.
    
    Args:
        agent: YonaAgent instance
        music_api: MusicAPI instance
        supabase_client: SupabaseClient instance
    """
    try:
        # Get unprocessed feedback
        unprocessed_feedback = supabase_client.get_unprocessed_feedback()
        
        if not unprocessed_feedback:
            logger.info("No unprocessed feedback found")
            return
        
        logger.info(f"Found {len(unprocessed_feedback)} unprocessed feedback records")
        
        # Process each feedback record
        for feedback in unprocessed_feedback:
            success = process_feedback(feedback, agent, music_api, supabase_client)
            if success:
                logger.info(f"Successfully processed feedback {feedback['id']}")
            else:
                logger.error(f"Failed to process feedback {feedback['id']}")
    
    except Exception as e:
        logger.error(f"Error checking for unprocessed feedback: {str(e)}")
        logger.exception("Exception details:")

def check_for_unprocessed_influence_music(agent, music_api, supabase_client):
    """
    Check for unprocessed influence music and process it.
    
    Args:
        agent: YonaAgent instance
        music_api: MusicAPI instance
        supabase_client: SupabaseClient instance
    """
    try:
        # Get unprocessed influence music
        unprocessed_records = supabase_client.get_unprocessed_influence_music()
        
        if not unprocessed_records:
            logger.info("No unprocessed influence music found")
            return
        
        logger.info(f"Found {len(unprocessed_records)} unprocessed influence music records")
        
        # Process each record
        for record in unprocessed_records:
            success = process_influence_music(record, agent, music_api, supabase_client)
            if success:
                logger.info(f"Successfully processed influence music {record['id']}")
            else:
                logger.error(f"Failed to process influence music {record['id']}")
    
    except Exception as e:
        logger.error(f"Error checking for unprocessed influence music: {str(e)}")
        logger.exception("Exception details:")

def main():
    """Run the continuous feedback processor."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Create agent, music API, and Supabase client
        agent = YonaAgent()
        music_api = MusicAPI()
        supabase_client = SupabaseClient()
        
        # Check for unprocessed feedback immediately
        logger.info("Checking for unprocessed feedback...")
        check_for_unprocessed_feedback(agent, music_api, supabase_client)
        
        # Check for unprocessed influence music immediately
        logger.info("Checking for unprocessed influence music...")
        check_for_unprocessed_influence_music(agent, music_api, supabase_client)
        
        # Schedule checks every 30 minutes
        schedule.every(30).minutes.do(check_for_unprocessed_feedback, agent, music_api, supabase_client)
        schedule.every(30).minutes.do(check_for_unprocessed_influence_music, agent, music_api, supabase_client)
        
        logger.info("Continuous feedback processor started")
        print("Continuous feedback processor started")
        print("Press Ctrl+C to stop")
        
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Continuous feedback processor stopped by user")
        print("Continuous feedback processor stopped")
    
    except Exception as e:
        logger.error(f"Error running continuous feedback processor: {str(e)}")
        logger.exception("Exception details:")
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
