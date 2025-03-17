"""
Test script for creating a persona on MusicAPI.ai.
"""
import asyncio
import os
from dotenv import load_dotenv
from music_api import MusicAPI

async def test_persona_creation():
    """Test creating a persona on MusicAPI.ai."""
    print("Testing persona creation on MusicAPI.ai...")
    
    # Initialize the MusicAPI client
    music_api = MusicAPI()
    
    # Check if we have an API key
    if not music_api.api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    try:
        # Create a test persona
        print("\nCreating test persona...")
        persona = await music_api.create_persona(
            name="Test Persona",
            description="A test persona for K-pop music with bright EDM influences",
            continue_clip_id="a2632456-62b0-405c-9de8-2ba509cf24fe"  # Using the default clip ID
        )
        
        print("\nPersona created successfully!")
        print(f"Persona ID: {persona['id']}")
        print(f"Persona Name: {persona['name']}")
        print(f"Message: {persona.get('message', 'No message')}")
        
        return persona
    except Exception as e:
        print(f"\nError creating persona: {str(e)}")
        return None

if __name__ == "__main__":
    # Run the test
    persona = asyncio.run(test_persona_creation())
    
    if persona:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed.") 