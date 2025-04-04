"""
Supabase client for interacting with the database.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from supabase import create_client

from src.config.config import SUPABASE_URL, SUPABASE_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Client for interacting with Supabase to store and retrieve song data.
    """
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize the Supabase client.
        
        Args:
            url: Supabase URL (defaults to environment variable)
            key: Supabase key (defaults to environment variable)
        """
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        
        # Validate credentials
        if not self.url or not self.key:
            logger.error("Supabase credentials are missing! Cannot proceed without valid credentials.")
            raise ValueError("Supabase URL and key are required")
        
        # Initialize client
        try:
            self.client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {str(e)}")
            raise
    
    def store_song_data(self, song_data: Dict[str, Any]) -> str:
        """
        Store song data in Supabase.
        
        Args:
            song_data: Dictionary with song data including title, lyrics, audio_url, etc.
            
        Returns:
            The ID of the created song record
        """
        
        logger.info(f"Storing song data for '{song_data.get('title', 'Unknown')}' in Supabase")
        
        # Make a copy of the song_data to avoid modifying the original
        song_data_copy = song_data.copy()
        
        # Check if we need to handle voice_gender separately
        voice_gender = None
        
        # Remove voice_gender from song_data if it exists
        if 'voice_gender' in song_data_copy:
            voice_gender = song_data_copy.pop('voice_gender')
            
            # Add voice_gender to style or tags if needed
            if 'style' in song_data_copy and song_data_copy['style']:
                if f"{voice_gender} voice" not in song_data_copy['style']:
                    song_data_copy['style'] = f"{song_data_copy['style']}, {voice_gender} voice"
            else:
                song_data_copy['style'] = f"{voice_gender} voice"
        
        # Remove original_prompt from song_data if it exists
        if 'original_prompt' in song_data_copy:
            logger.info("Removing 'original_prompt' field from song data")
            song_data_copy.pop('original_prompt')
        
        # Check if params_used contains fields that might not exist in the database schema
        if 'params_used' in song_data_copy and isinstance(song_data_copy['params_used'], dict):
            params = song_data_copy['params_used']
            # Fields to remove from params_used
            fields_to_remove = ['original_prompt', 'song_concept', 'concept']
            for field in fields_to_remove:
                if field in params:
                    logger.info(f"Removing '{field}' field from params_used")
                    params.pop(field)
            
            # Convert the concept to a string if it exists
            if 'concept' in params and not isinstance(params['concept'], str):
                try:
                    params['concept'] = json.dumps(params['concept'])
                except:
                    logger.warning("Could not convert concept to string, removing it")
                    params.pop('concept')
        
        try:
            response = self.client.table("songs").insert(song_data_copy).execute()
            
            if response.data and len(response.data) > 0:
                song_id = response.data[0].get('id')
                logger.info(f"Song data stored successfully with ID: {song_id}")
                return song_id
            else:
                logger.error("No data returned from Supabase insert operation")
                return None
                
        except Exception as e:
            logger.error(f"Error storing song data: {str(e)}")
            return None
    
    def get_song_by_id(self, song_id: str) -> Dict[str, Any]:
        """
        Retrieve a song by its ID.
        
        Args:
            song_id: The ID of the song to retrieve
            
        Returns:
            Dictionary with song data, or None if not found
        """
        
        logger.info(f"Retrieving song with ID: {song_id}")
        
        try:
            response = self.client.table("songs").select("*").eq("id", song_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Retrieved song: {response.data[0].get('title')}")
                return response.data[0]
            else:
                logger.warning(f"No song found with ID: {song_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving song: {str(e)}")
            return None
    
    def list_songs(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List songs from the database.
        
        Args:
            limit: Maximum number of songs to return
            offset: Offset for pagination
            
        Returns:
            List of song data dictionaries
        """
        
        logger.info(f"Listing songs (limit: {limit}, offset: {offset})")
        
        try:
            response = self.client.table("songs").select("*").order("created_at", desc=True).limit(limit).offset(offset).execute()
            
            if response.data:
                logger.info(f"Retrieved {len(response.data)} songs")
                return response.data
            else:
                logger.warning("No songs found")
                return []
                
        except Exception as e:
            logger.error(f"Error listing songs: {str(e)}")
            return []
    
    def get_feedback_by_id(self, feedback_id: str) -> Dict[str, Any]:
        """
        Retrieve feedback by its ID.
        
        Args:
            feedback_id: The ID of the feedback to retrieve
            
        Returns:
            Dictionary with feedback data, or None if not found
        """
        
        logger.info(f"Retrieving feedback with ID: {feedback_id}")
        
        try:
            response = self.client.table("feedback").select("*").eq("id", feedback_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Retrieved feedback for song: {response.data[0].get('song_id')}")
                return response.data[0]
            else:
                logger.warning(f"No feedback found with ID: {feedback_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving feedback: {str(e)}")
            return None
    
    def update_feedback(self, feedback_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a feedback record.
        
        Args:
            feedback_id: The ID of the feedback to update
            data: Dictionary with fields to update
            
        Returns:
            True if successful, False otherwise
        """
        
        logger.info(f"Updating feedback {feedback_id}")
        
        try:
            response = self.client.table("feedback").update(data).eq("id", feedback_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Updated feedback: {feedback_id}")
                return True
            else:
                logger.warning(f"No feedback updated with ID: {feedback_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating feedback: {str(e)}")
            return False
    
    def get_unprocessed_feedback(self) -> List[Dict[str, Any]]:
        """
        Get all feedback records that haven't been processed yet (rating is NULL).
        
        Returns:
            List of unprocessed feedback records
        """
        
        logger.info("Retrieving unprocessed feedback (where rating is NULL)")
        
        try:
            # Query feedback table for records where rating is NULL
            response = self.client.table("feedback").select("*").is_("rating", "null").execute()
            
            if response.data:
                logger.info(f"Found {len(response.data)} unprocessed feedback records")
                return response.data
            else:
                logger.info("No unprocessed feedback found")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving unprocessed feedback: {str(e)}")
            return []
    
    def store_song_version(self, original_song_id: str, version_data: Dict[str, Any]) -> str:
        """
        Store a new version of a song in the song_versions table.
        
        Args:
            original_song_id: ID of the original song
            version_data: Dictionary with version data
                
        Returns:
            The ID of the created song version record
        """
        
        logger.info(f"Storing song version for song {original_song_id}")
        
        try:
            # Get the highest current version number for this song
            response = self.client.table("song_versions").select("version_number").eq("song_id", original_song_id).order("version_number", desc=True).limit(1).execute()
            
            # Determine the next version number
            next_version = 1
            if response.data and len(response.data) > 0:
                next_version = response.data[0].get('version_number', 0) + 1
            
            # Prepare the data for insertion
            insert_data = {
                'song_id': original_song_id,
                'version_number': next_version,
                'title': version_data.get('title'),
                'lyrics': version_data.get('lyrics'),
                'audio_url': version_data.get('audio_url'),
                'params_used': version_data.get('params_used')
            }
            
            # Insert the record
            response = self.client.table("song_versions").insert(insert_data).execute()
            
            if response.data and len(response.data) > 0:
                version_id = response.data[0].get('id')
                logger.info(f"Song version stored successfully with ID: {version_id} (version {next_version})")
                return version_id
            else:
                logger.error("No data returned from Supabase insert operation")
                return None
                
        except Exception as e:
            logger.error(f"Error storing song version: {str(e)}")
            return None
    
    def get_unprocessed_influence_music(self, limit: int = 1) -> List[Dict[str, Any]]:
        """
        Get unprocessed influence_music records (those with NULL song_id).
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of unprocessed influence_music records
        """
        try:
            response = self.client.table("influence_music").select("*").is_("song_id", "null").limit(limit).execute()
            
            if response.data:
                logger.info(f"Found {len(response.data)} unprocessed influence_music records")
                return response.data
            else:
                logger.info("No unprocessed influence_music records found")
                return []
                
        except Exception as e:
            logger.error(f"Error getting unprocessed influence_music records: {str(e)}")
            return []
    
    def mark_influence_music_processed(self, record_id: str, song_id: str) -> bool:
        """
        Mark an influence_music record as processed by setting its song_id.
        
        Args:
            record_id: ID of the record to mark as processed
            song_id: ID of the song created from this record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the song_id field
            response = self.client.table("influence_music").update({"song_id": song_id}).eq("id", record_id).execute()
            
            if response.data:
                logger.info(f"Influence music record {record_id} marked as processed with song_id {song_id}")
                return True
            else:
                logger.warning(f"Failed to mark influence music record {record_id} as processed")
                return False
                
        except Exception as e:
            logger.error(f"Error marking influence music record as processed: {str(e)}")
            return False
