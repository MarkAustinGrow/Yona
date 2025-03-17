"""
Test script for creating a song on MusicAPI.ai.
"""
import asyncio
import os
from dotenv import load_dotenv
from music_api import MusicAPI

async def test_song_creation(persona_id=None):
    """
    Test creating a song on MusicAPI.ai.
    
    Args:
        persona_id (str, optional): The ID of the persona to use. If None, a new persona will be created.
    """
    print("Testing song creation on MusicAPI.ai...")
    
    # Initialize the MusicAPI client
    music_api = MusicAPI()
    
    # Check if we have an API key
    if not music_api.api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    try:
        # Create a persona if none is provided
        if not persona_id:
            print("\nNo persona ID provided. Creating a new persona...")
            persona = await music_api.create_persona(
                name="Test Persona",
                description="A test persona for K-pop music with bright EDM influences",
                continue_clip_id="a2632456-62b0-405c-9de8-2ba509cf24fe"  # Using the default clip ID
            )
            persona_id = persona['id']
            print(f"Created persona with ID: {persona_id}")
        
        # Sample lyrics for testing
        lyrics = """
        [Verse 1]
        Bright lights in the city tonight
        Feel the rhythm, feel it right
        Dancing through the neon glow
        Energy high, never low
        
        [Pre-Chorus]
        Heartbeat racing to the beat
        This moment makes me feel complete
        
        [Chorus]
        Electric dreams, electric nights
        K-pop vibes taking flight
        Synth waves crashing over me
        This is where I want to be
        
        [Verse 2]
        Midnight streets, we're running free
        Creating memories, you and me
        Voices echo through the air
        Living life without a care
        
        [Pre-Chorus]
        Heartbeat racing to the beat
        This moment makes me feel complete
        
        [Chorus]
        Electric dreams, electric nights
        K-pop vibes taking flight
        Synth waves crashing over me
        This is where I want to be
        
        [Bridge]
        Breaking through, breaking through
        Nothing can stop what we do
        Feel the power, feel the rush
        This energy we cannot crush
        
        [Chorus]
        Electric dreams, electric nights
        K-pop vibes taking flight
        Synth waves crashing over me
        This is where I want to be
        """
        
        # Create a song
        print("\nCreating test song...")
        song = await music_api.create_song(
            persona_id=persona_id,
            prompt=lyrics,
            style="kpop",
            title="Electric Dreams"
        )
        
        print("\nSong created successfully!")
        print(f"Song ID: {song['id']}")
        print(f"Audio URL: {song['audio_url']}")
        
        return song
    except Exception as e:
        print(f"\nError creating song: {str(e)}")
        return None

if __name__ == "__main__":
    # Get persona ID from command line if provided
    import sys
    persona_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the test
    song = asyncio.run(test_song_creation(persona_id))
    
    if song:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed.") 