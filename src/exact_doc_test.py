"""
Test script that exactly matches the documentation screenshot for creating a persona.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_persona_creation():
    """Test creating a persona using the exact format from the documentation screenshot."""
    print("Testing persona creation with exact documentation format...")
    
    try:
        url = "https://api.musicapi.ai/api/v1/sonic/persona"
        
        # Use the exact continue_clip_id from the screenshot
        payload = {
            "name": "test persona",
            "description": "Pop, rap, rhythmic male bass",
            "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
        }
        
        # Get the API key
        api_key = os.getenv("MUSICAPI_KEY")
        if not api_key:
            print("Error: No MusicAPI key found. Please check your .env file.")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        print("\nSending request to create persona...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Headers: Content-Type: application/json, Authorization: Bearer [REDACTED]")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        return response.text
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        return None

if __name__ == "__main__":
    # Run the test
    result = test_persona_creation()
    
    if result:
        print("\nTest completed!")
    else:
        print("\nTest failed.") 