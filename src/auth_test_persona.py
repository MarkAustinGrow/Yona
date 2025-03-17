"""
Test script that tries different formats of the Authorization header.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_persona_creation_with_auth_format(auth_format):
    """
    Test creating a persona with a specific Authorization header format.
    
    Args:
        auth_format (str): The format of the Authorization header.
    """
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
            'Authorization': auth_format.format(api_key=api_key)
        }
        
        print(f"\nTrying Authorization format: {auth_format.format(api_key='[REDACTED]')}")
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        return response.status_code, response.text
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, str(e)

def main():
    """Test different Authorization header formats."""
    print("Testing persona creation with different Authorization header formats...")
    
    # Different formats to try
    auth_formats = [
        "Bearer {api_key}",                  # Standard Bearer token
        "{api_key}",                         # Just the key
        "Token {api_key}",                   # Token prefix
        "ApiKey {api_key}",                  # ApiKey prefix
        "Basic {api_key}",                   # Basic prefix
        "key={api_key}",                     # key=value format
        "api_key={api_key}"                  # api_key=value format
    ]
    
    # Try each format
    for auth_format in auth_formats:
        status_code, response_text = test_persona_creation_with_auth_format(auth_format)
        
        # If we get a successful response, stop trying
        if status_code == 200:
            print(f"\nSuccess with format: {auth_format}")
            break
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 