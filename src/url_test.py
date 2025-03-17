"""
Test script that tries different URL structures.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_persona_creation(url):
    """
    Test creating a persona with a specific URL.
    
    Args:
        url (str): The URL to use for the request
    """
    print(f"Testing persona creation with URL: {url}")
    
    # Get the API key
    api_key = os.getenv("MUSICAPI_KEY")
    if not api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    try:
        payload = {
            "name": "test persona",
            "description": "Pop, rap, rhythmic male bass",
            "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        return response.status_code, response.text
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, str(e)

def main():
    """Test different URL structures."""
    print("Testing persona creation with different URL structures...")
    
    # Different URLs to try
    urls = [
        "https://api.musicapi.ai/api/v1/sonic/persona",
        "https://api.musicapi.ai/api/v1/sonic/personas",
        "https://api.musicapi.ai/api/v1/sonic/create-persona",
        "https://api.musicapi.ai/api/v1/persona",
        "https://api.musicapi.ai/api/v1/personas",
        "https://api.musicapi.ai/api/sonic/persona",
        "https://api.musicapi.ai/sonic/persona",
        "https://musicapi.ai/api/v1/sonic/persona"
    ]
    
    # Try each URL
    for url in urls:
        print("\n" + "="*50)
        status_code, response_text = test_persona_creation(url)
        
        # If we get a successful response, stop trying
        if status_code == 200:
            print(f"\nSuccess with URL: {url}")
            break
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 