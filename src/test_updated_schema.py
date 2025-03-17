#!/usr/bin/env python
"""
Test script to verify that the updated supabase_client.py works with the new schema.
This script creates a test song with parameters that will be stored in the dedicated columns.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_updated_schema():
    """Test the updated schema by creating a test song."""
    # Create a Supabase client
    client = SupabaseClient(simulation_mode=False)
    
    # Create test song data
    title = "Test Song with New Schema"
    persona_id = "test_persona"
    lyrics = "[Verse 1]\nThis is a test song\nTo verify the schema update\n\n[Chorus]\nStoring parameters in dedicated columns\nMakes querying much easier"
    audio_url = "https://example.com/test-song.mp3"
    
    # Create test parameters with values for all dedicated columns
    params_used = {
        "style": "kpop, test",
        "mv": "sonic-v4",
        "negative_tags": "noise, distortion",
        "make_instrumental": True,
        "gpt_description_prompt": "A test song to verify the schema update",
        "image_url": "https://example.com/test-image.jpg",
        "video_url": "https://example.com/test-video.mp4",
        "duration": 180.5,
        "extra_param1": "This will only be in the JSONB field",
        "extra_param2": "This will also only be in the JSONB field"
    }
    
    # Store the song data
    logger.info(f"Storing test song '{title}' with parameters for dedicated columns")
    result = await client.store_song_data(title, persona_id, lyrics, audio_url, params_used)
    
    if "error" in result:
        logger.error(f"Error storing test song: {result['error']}")
    else:
        logger.info(f"Test song stored successfully with ID: {result.get('id')}")
        logger.info("Parameters should now be stored in both dedicated columns and params_used JSONB field")

if __name__ == "__main__":
    asyncio.run(test_updated_schema()) 