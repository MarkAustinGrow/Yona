"""
Database integration with Supabase for storing song data.
"""
import os
from supabase import create_client
from dotenv import load_dotenv
from config.config import SUPABASE_URL, SUPABASE_KEY

load_dotenv()

class Database:
    """Database class for interacting with Supabase."""
    
    def __init__(self):
        """Initialize the database connection."""
        # Load from config
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        
        # For now, we'll just print a message since we don't have actual Supabase credentials
        if not self.url or not self.key:
            print("Warning: Supabase credentials not found. Database operations will be simulated.")
            self.client = None
        else:
            self.client = create_client(self.url, self.key)
    
    def store_song(self, title, persona_id, lyrics, audio_url, params_used):
        """
        Store a song in the database.
        
        Args:
            title (str): The title of the song
            persona_id (str): The ID of the persona used to create the song
            lyrics (str): The lyrics of the song
            audio_url (str): The URL of the generated audio
            params_used (dict): The parameters used to generate the song
        
        Returns:
            dict: The created record or a simulated response
        """
        if self.client:
            response = self.client.table("songs").insert({
                "title": title,
                "persona_id": persona_id,
                "lyrics": lyrics,
                "audio_url": audio_url,
                "params_used": params_used
            }).execute()
            return response.data[0] if response.data else {"id": "error", "error": "Failed to insert song"}
        else:
            # Simulate a response
            print(f"Simulated: Stored song '{title}' in database")
            return {
                "id": "simulated-id",
                "title": title,
                "persona_id": persona_id,
                "created_at": "simulated-timestamp"
            }
    
    def get_songs(self, limit=10):
        """
        Get a list of songs from the database.
        
        Args:
            limit (int): The maximum number of songs to retrieve
        
        Returns:
            list: A list of song records
        """
        if self.client:
            response = self.client.table("songs").select("*").limit(limit).execute()
            return response.data
        else:
            # Simulate a response
            print(f"Simulated: Retrieved {limit} songs from database")
            return [{"id": "simulated-id", "title": "Simulated Song"}]
    
    def store_persona(self, external_id, name, description):
        """
        Store a persona in the database.
        
        Args:
            external_id (str): The external ID of the persona (from MusicAPI)
            name (str): The name of the persona
            description (str): The description of the persona
        
        Returns:
            dict: The created record or a simulated response
        """
        if self.client:
            response = self.client.table("personas").insert({
                "external_id": external_id,
                "name": name,
                "description": description
            }).execute()
            return response.data[0] if response.data else {"id": "error", "error": "Failed to insert persona"}
        else:
            # Simulate a response
            print(f"Simulated: Stored persona '{name}' in database")
            return {
                "id": "simulated-id",
                "external_id": external_id,
                "name": name,
                "created_at": "simulated-timestamp"
            }
    
    def get_persona_by_external_id(self, external_id):
        """
        Get a persona by its external ID.
        
        Args:
            external_id (str): The external ID of the persona
        
        Returns:
            dict: The persona record or None if not found
        """
        if self.client:
            response = self.client.table("personas").select("*").eq("external_id", external_id).execute()
            return response.data[0] if response.data else None
        else:
            # Simulate a response
            print(f"Simulated: Retrieved persona with external ID '{external_id}' from database")
            return {
                "id": "simulated-id",
                "external_id": external_id,
                "name": "Simulated Persona",
                "created_at": "simulated-timestamp"
            }
    
    def store_song_version(self, song_id, version_number, title, lyrics, audio_url, params_used):
        """
        Store a song version in the database.
        
        Args:
            song_id (str): The ID of the parent song
            version_number (int): The version number
            title (str): The title of the song version
            lyrics (str): The lyrics of the song version
            audio_url (str): The URL of the generated audio
            params_used (dict): The parameters used to generate the song version
        
        Returns:
            dict: The created record or a simulated response
        """
        if self.client:
            response = self.client.table("song_versions").insert({
                "song_id": song_id,
                "version_number": version_number,
                "title": title,
                "lyrics": lyrics,
                "audio_url": audio_url,
                "params_used": params_used
            }).execute()
            return response.data[0] if response.data else {"id": "error", "error": "Failed to insert song version"}
        else:
            # Simulate a response
            print(f"Simulated: Stored version {version_number} of song '{title}' in database")
            return {
                "id": "simulated-id",
                "song_id": song_id,
                "version_number": version_number,
                "title": title,
                "created_at": "simulated-timestamp"
            }
    
    def get_song_versions(self, song_id):
        """
        Get all versions of a song.
        
        Args:
            song_id (str): The ID of the song
        
        Returns:
            list: A list of song version records
        """
        if self.client:
            response = self.client.table("song_versions").select("*").eq("song_id", song_id).order("version_number").execute()
            return response.data
        else:
            # Simulate a response
            print(f"Simulated: Retrieved versions of song with ID '{song_id}' from database")
            return [{"id": "simulated-id", "song_id": song_id, "version_number": 1, "title": "Simulated Song Version"}]
    
    def store_feedback(self, song_id, rating, comments=None):
        """
        Store feedback for a song.
        
        Args:
            song_id (str): The ID of the song
            rating (int): The rating (1-5)
            comments (str, optional): Additional comments
        
        Returns:
            dict: The created record or a simulated response
        """
        if self.client:
            response = self.client.table("feedback").insert({
                "song_id": song_id,
                "rating": rating,
                "comments": comments
            }).execute()
            return response.data[0] if response.data else {"id": "error", "error": "Failed to insert feedback"}
        else:
            # Simulate a response
            print(f"Simulated: Stored feedback for song with ID '{song_id}' in database")
            return {
                "id": "simulated-id",
                "song_id": song_id,
                "rating": rating,
                "created_at": "simulated-timestamp"
            }
    
    def get_feedback_for_song(self, song_id):
        """
        Get all feedback for a song.
        
        Args:
            song_id (str): The ID of the song
        
        Returns:
            list: A list of feedback records
        """
        if self.client:
            response = self.client.table("feedback").select("*").eq("song_id", song_id).execute()
            return response.data
        else:
            # Simulate a response
            print(f"Simulated: Retrieved feedback for song with ID '{song_id}' from database")
            return [{"id": "simulated-id", "song_id": song_id, "rating": 5, "comments": "Simulated feedback"}] 