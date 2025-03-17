"""
Configuration for the Yona project.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_KEY = os.getenv("OPENAI_KEY")
OPENAI_MODEL = "gpt-4"

# MusicAPI.ai configuration
MUSICAPI_KEY = os.getenv("MUSICAPI_KEY")
MUSICAPI_BASE_URL = "https://api.musicapi.ai"

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# YouTube API configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")

# Yona persona configuration
YONA_PERSONA = {
    "name": "Yona",
    "description": "Energetic K-pop idol persona with bright EDM influences, occasionally rapping segments.",
    "style": "kpop",
    "personality_traits": [
        "Energetic",
        "Positive",
        "Creative",
        "Emotional",
        "Authentic"
    ]
}

# Default song parameters
DEFAULT_SONG_PARAMETERS = {
    "tempo": 120,
    "duration": 180
} 