import os
from dotenv import load_dotenv
import json
import logging
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SupabaseClient:
    """Client for interacting with Supabase."""
    
    def __init__(self, simulation_mode=True):
        """
        Initialize the Supabase client.
        
        Args:
            simulation_mode (bool): Whether to simulate Supabase operations
        """
        self.simulation_mode = simulation_mode
        
        # Get Supabase credentials from environment variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Initialize Supabase client if not in simulation mode
        if not simulation_mode and self.supabase_url and self.supabase_key:
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized")
        else:
            self.client = None
            if simulation_mode:
                logger.info("Supabase client initialized in simulation mode")
            else:
                logger.warning("Supabase credentials missing - using simulation mode")
    
    async def store_song_data(self, title, persona_id, lyrics, audio_url, params_used):
        """
        Store song data in Supabase.
        
        Args:
            title (str): Song title
            persona_id (str): ID of the persona used to create the song
            lyrics (str): Song lyrics
            audio_url (str): URL to the generated audio
            params_used (dict): Parameters used to generate the song
            
        Returns:
            dict: The stored song data or a simulated response
        """
        if self.simulation_mode or not self.client:
            logger.info(f"SIMULATION: Storing song data for '{title}'")
            return self._simulate_store_song(title, persona_id, lyrics, audio_url, params_used)
        
        try:
            # Prepare the data to insert
            song_data = {
                "title": title,
                "persona_id": persona_id,
                "lyrics": lyrics,
                "audio_url": audio_url,
                "params_used": json.dumps(params_used)  # Convert dict to JSON string
            }
            
            # Insert the data into the songs table
            logger.info(f"Storing song data for '{title}' in Supabase")
            response = self.client.table("songs").insert(song_data).execute()
            
            # Check if the insert was successful
            if response.data:
                logger.info(f"Song data stored successfully with ID: {response.data[0]['id']}")
                return response.data[0]
            else:
                logger.error(f"Error storing song data: {response.error}")
                return {"error": response.error}
                
        except Exception as e:
            logger.error(f"Exception during song data storage: {str(e)}")
            return {"error": str(e)}
    
    def _simulate_store_song(self, title, persona_id, lyrics, audio_url, params_used):
        """
        Simulate storing song data for testing without Supabase.
        
        Args:
            title (str): Song title
            persona_id (str): ID of the persona used to create the song
            lyrics (str): Song lyrics
            audio_url (str): URL to the generated audio
            params_used (dict): Parameters used to generate the song
            
        Returns:
            dict: Simulated Supabase response
        """
        logger.info("Generating simulated Supabase response")
        
        # Create a simulated response
        return {
            "id": "sim_song_id_12345",
            "title": title,
            "persona_id": persona_id,
            "lyrics": lyrics,
            "audio_url": audio_url,
            "params_used": params_used,
            "created_at": "2023-06-15T12:00:00Z",
            "status": "simulated"
        } 