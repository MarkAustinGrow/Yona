"""
Test script that tries different API key formats.
"""
import requests
import json
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def format_api_key(api_key, format_type):
    """
    Format the API key in different ways.
    
    Args:
        api_key (str): The original API key
        format_type (str): The type of formatting to apply
    
    Returns:
        str: The formatted API key
    """
    if format_type == "original":
        return api_key
    elif format_type == "uuid":
        # Try to format as UUID if possible
        try:
            # If it's a 32-character hex string, format it as UUID
            if len(api_key) == 32 and all(c in "0123456789abcdef" for c in api_key.lower()):
                return f"{api_key[:8]}-{api_key[8:12]}-{api_key[12:16]}-{api_key[16:20]}-{api_key[20:]}"
            return api_key
        except:
            return api_key
    elif format_type == "example":
        # Use the example from the documentation
        return "2f68dbbf-519d-4f01-9636-e2421b68f379"
    return api_key

def test_persona_creation(api_key_format):
    """
    Test creating a persona with a specific API key format.
    
    Args:
        api_key_format (str): The format to use for the API key
    """
    print(f"Testing persona creation with API key format: {api_key_format}")
    
    # Get the API key
    api_key = os.getenv("MUSICAPI_KEY")
    if not api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    # Format the API key
    formatted_key = format_api_key(api_key, api_key_format)
    
    try:
        url = "https://api.musicapi.ai/api/v1/sonic/persona"
        
        payload = {
            "name": "test persona",
            "description": "Pop, rap, rhythmic male bass",
            "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {formatted_key}'
        }
        
        print(f"\nUsing API key: {formatted_key[:4]}...{formatted_key[-4:]} (formatted as {api_key_format})")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        return response.status_code, response.text
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, str(e)

def main():
    """Test different API key formats."""
    print("Testing persona creation with different API key formats...")
    
    # Different formats to try
    api_key_formats = [
        "original",  # Use the key as-is
        "uuid",      # Format as UUID if possible
        "example"    # Use the example from the documentation
    ]
    
    # Try each format
    for api_key_format in api_key_formats:
        print("\n" + "="*50)
        status_code, response_text = test_persona_creation(api_key_format)
        
        # If we get a successful response, stop trying
        if status_code == 200:
            print(f"\nSuccess with format: {api_key_format}")
            break
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 