#!/usr/bin/env python
"""
Yona Implementation Manager

This module manages the Yona implementation and provides methods to access its functionality.
It serves as a bridge between CrewAI and the Yona codebase.
"""
import logging
import json
from src.agent import YonaAgent
from crew_config import OPENAI_KEY

logger = logging.getLogger(__name__)

class YonaImplementationManager:
    """
    Manages the Yona implementation and provides methods to access its functionality.
    This class serves as a bridge between CrewAI and the Yona codebase.
    """
    
    def __init__(self, did_domain="yona.ai", private_key_path=None):
        """Initialize the Yona implementation manager"""
        logger.info("Initializing Yona Implementation Manager")
        
        try:
            # Initialize the actual Yona implementation
            self.yona = YonaAgent(
                openai_api_key=OPENAI_KEY,
                did_domain=did_domain,
                private_key_path=private_key_path
            )
            logger.info(f"Yona agent initialized with DID: {self.yona.did_manager.did}")
        except Exception as e:
            logger.error(f"Failed to initialize Yona agent: {str(e)}")
            raise
    
    def generate_song(self, prompt, api="sonic", **kwargs):
        """
        Generate a song based on a prompt
        
        Args:
            prompt: The prompt describing the song to create
            api: Which API to use ('sonic' or 'nuro')
            **kwargs: Additional parameters for song creation
            
        Returns:
            Dictionary containing the song data, including URLs and metadata
        """
        logger.info(f"Generating song from prompt: {prompt} using {api} API")
        
        try:
            # Generate song concept
            concept = self.yona.generate_song_concept(prompt)
            logger.info(f"Generated concept: {concept.get('title')}")
            
            # Generate lyrics
            lyrics = self.yona.generate_lyrics(concept)
            logger.info(f"Generated lyrics (excerpt): {lyrics[:50]}...")
            
            # Extract parameters from the concept
            title = concept.get('title')
            style = concept.get('style_tags')
            negative_tags = concept.get('negative_tags')
            make_instrumental = concept.get('make_instrumental', False)
            mv = concept.get('mv_type', 'sonic-v4')
            description = concept.get('description', '')
            
            # Override parameters if provided in kwargs
            title = kwargs.get('title', title)
            style = kwargs.get('style', style)
            negative_tags = kwargs.get('negative_tags', negative_tags)
            make_instrumental = kwargs.get('make_instrumental', make_instrumental)
            mv = kwargs.get('mv', mv)
            description = kwargs.get('description', description)
            
            # Create the song using the appropriate API
            if api == "nuro":
                # Extract Nuro-specific parameters
                gender = kwargs.get('gender', concept.get('gender', 'Female'))
                genre = kwargs.get('genre', concept.get('genre', 'Pop'))
                mood = kwargs.get('mood', concept.get('mood', 'Happy'))
                timbre = kwargs.get('timbre', concept.get('timbre', 'Powerful'))
                duration = kwargs.get('duration', concept.get('duration', 60))
                
                # Create song with Nuro API
                song = self.yona.create_song(
                    title=title,
                    lyrics=lyrics,
                    api='nuro',
                    gender=gender,
                    genre=genre,
                    mood=mood,
                    timbre=timbre,
                    duration=duration,
                    mv=mv
                )
            else:
                # Create song with Sonic API
                song = self.yona.create_song(
                    title=title,
                    lyrics=lyrics,
                    style=style,
                    negative_tags=negative_tags,
                    make_instrumental=make_instrumental,
                    mv=mv,
                    gpt_description_prompt=description,
                    voice_gender=kwargs.get('voice_gender', 'female')
                )
            
            # Add concept and lyrics to the result
            if song.get('status') != 'failed':
                song['concept'] = concept
                song['lyrics'] = lyrics
            
            return song
            
        except Exception as e:
            logger.error(f"Error generating song: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "prompt": prompt
            }
    
    def process_feedback(self, song_id, feedback_id):
        """
        Process feedback for a song
        
        Args:
            song_id: ID of the original song
            feedback_id: ID of the feedback to process
            
        Returns:
            Dictionary containing the new song data
        """
        logger.info(f"Processing feedback {feedback_id} for song {song_id}")
        
        try:
            # Get the original song
            original_song = self.yona.supabase_client.get_song_by_id(song_id)
            if not original_song:
                logger.error(f"Original song {song_id} not found")
                return {"status": "failed", "error": f"Original song {song_id} not found"}
            
            # Get the feedback
            feedback = self.yona.supabase_client.get_feedback_by_id(feedback_id)
            if not feedback:
                logger.error(f"Feedback {feedback_id} not found")
                return {"status": "failed", "error": f"Feedback {feedback_id} not found"}
            
            # Extract parameters from the original song
            original_params = original_song.get('params_used', {})
            if not original_params:
                logger.warning(f"No params_used found for song {song_id}, using defaults")
                original_params = {
                    'prompt': original_song.get('lyrics', ''),
                    'title': original_song.get('title', 'Untitled'),
                    'style': original_song.get('style', ''),
                    'negative_tags': original_song.get('negative_tags', ''),
                    'make_instrumental': original_song.get('make_instrumental', False),
                    'mv': original_song.get('mv', 'sonic-v4'),
                    'gpt_description_prompt': original_song.get('gpt_description', ''),
                    'voice_gender': 'female'
                }
            
            # Modify parameters based on feedback
            modified_params = self._modify_parameters_with_openai(original_params, feedback.get('comments', ''))
            
            # Create a new song with the modified parameters
            api_to_use = original_params.get('api_used', 'sonic')
            
            if api_to_use == 'nuro':
                # Create song with Nuro API
                new_song = self.yona.create_song(
                    title=modified_params.get('title'),
                    lyrics=modified_params.get('prompt'),  # For Nuro, prompt contains lyrics
                    api='nuro',
                    gender=modified_params.get('gender', 'Female'),
                    genre=modified_params.get('genre', 'Pop'),
                    mood=modified_params.get('mood', 'Happy'),
                    timbre=modified_params.get('timbre', 'Powerful'),
                    duration=modified_params.get('duration', 60),
                    mv=modified_params.get('mv', 'sonic-v4')
                )
            else:
                # Create song with Sonic API
                new_song = self.yona.create_song(
                    title=modified_params.get('title'),
                    lyrics=modified_params.get('prompt'),
                    style=modified_params.get('style'),
                    negative_tags=modified_params.get('negative_tags'),
                    make_instrumental=modified_params.get('make_instrumental', False),
                    mv=modified_params.get('mv', 'sonic-v4'),
                    gpt_description_prompt=modified_params.get('gpt_description_prompt'),
                    voice_gender=modified_params.get('voice_gender', 'female')
                )
            
            # If successful, update the feedback record
            if new_song.get('status') != 'failed':
                # Add references to original song and feedback
                new_song['original_song_id'] = song_id
                new_song['feedback_id'] = feedback_id
                
                # Update the feedback record
                self.yona.supabase_client.update_feedback(feedback_id, {
                    'rating': 5,  # Mark as processed with a default rating
                    'processed_at': 'now()',
                    'new_song_id': new_song.get('id')
                })
                
                # Store as a version in the song_versions table
                version_data = {
                    'song_id': song_id,
                    'title': new_song.get('title'),
                    'lyrics': new_song.get('lyrics'),
                    'audio_url': new_song.get('audio_url'),
                    'params_used': modified_params
                }
                self.yona.supabase_client.store_song_version(song_id, version_data)
            
            return new_song
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "song_id": song_id,
                "feedback_id": feedback_id
            }
    
    def list_songs(self, limit=10, offset=0):
        """
        List songs from the database
        
        Args:
            limit: Maximum number of songs to return
            offset: Offset for pagination
            
        Returns:
            List of dictionaries containing song data
        """
        logger.info(f"Listing songs (limit: {limit}, offset: {offset})")
        
        try:
            return self.yona.list_songs(limit=limit, offset=offset)
        except Exception as e:
            logger.error(f"Error listing songs: {str(e)}")
            return []
    
    def get_song(self, song_id):
        """
        Get a specific song by ID
        
        Args:
            song_id: ID of the song to retrieve
            
        Returns:
            Dictionary containing the song data
        """
        logger.info(f"Getting song {song_id}")
        
        try:
            song = self.yona.supabase_client.get_song_by_id(song_id)
            if not song:
                logger.error(f"Song {song_id} not found")
                return {"status": "failed", "error": f"Song {song_id} not found"}
            return song
        except Exception as e:
            logger.error(f"Error getting song: {str(e)}")
            return {"status": "failed", "error": str(e), "song_id": song_id}
    
    def get_capability_document(self):
        """
        Get the capability document for the agent
        
        Returns:
            Dictionary containing the capability document
        """
        logger.info("Getting capability document")
        
        try:
            return self.yona.get_capability_document()
        except Exception as e:
            logger.error(f"Error getting capability document: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def get_did_document(self):
        """
        Get the DID document for the agent
        
        Returns:
            Dictionary containing the DID document
        """
        logger.info("Getting DID document")
        
        try:
            return self.yona.get_did_document()
        except Exception as e:
            logger.error(f"Error getting DID document: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def process_user_request(self, user_input):
        """
        Process a natural language request from the user
        
        Args:
            user_input: String containing the user's request
            
        Returns:
            Dictionary with results and response
        """
        logger.info(f"Processing user request: {user_input}")
        
        try:
            return self.yona.process_user_request(user_input)
        except Exception as e:
            logger.error(f"Error processing user request: {str(e)}")
            return {
                'action': 'error',
                'result': None,
                'response': f"Error processing request: {str(e)}"
            }
    
    def _modify_parameters_with_openai(self, original_params, feedback_comments):
        """
        Modify song parameters based on feedback using OpenAI
        
        Args:
            original_params: Original parameters used to create the song
            feedback_comments: User feedback comments
            
        Returns:
            Modified parameters
        """
        logger.info("Modifying parameters based on feedback")
        
        try:
            # Use OpenAI to modify parameters based on feedback
            system_message = """
            You are an AI assistant that helps modify song generation parameters based on user feedback.
            Analyze the feedback and suggest modifications to the original parameters.
            Return a JSON object with the modified parameters.
            """
            
            user_message = f"""
            Original parameters:
            {json.dumps(original_params, indent=2)}
            
            User feedback:
            {feedback_comments}
            
            Please modify the parameters based on the feedback. Return only the JSON object with the modified parameters.
            """
            
            response = self.yona.openai_client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Parse the response
            modified_params_text = response.choices[0].message.content
            modified_params = json.loads(modified_params_text)
            
            logger.info("Parameters modified successfully")
            return modified_params
            
        except Exception as e:
            logger.error(f"Error modifying parameters: {str(e)}")
            # Return original parameters if modification fails
            return original_params
