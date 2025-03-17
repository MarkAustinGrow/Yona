"""
Test script using the requests library example from the documentation.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_persona_creation():
    """Test creating a persona using the requests library example from the documentation."""
    print("Testing persona creation with requests library...")
    
    # Get the API key
    api_key = os.getenv("MUSICAPI_KEY")
    if not api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    try:
        url = "https://api.musicapi.ai/api/v1/sonic/persona"
        
        payload = json.dumps({
            "name": "test persona",
            "description": "Pop, rap, rhythmic male bass",
            "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        print("\nSending request to create persona...")
        response = requests.request("POST", url, headers=headers, data=payload)
        
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