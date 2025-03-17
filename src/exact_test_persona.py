"""
Test script that exactly matches the documentation example for creating a persona.
"""
import http.client
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_persona_creation():
    """Test creating a persona using the exact code from the documentation."""
    print("Testing persona creation with exact documentation code...")
    
    # Get the API key
    api_key = os.getenv("MUSICAPI_KEY")
    if not api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    try:
        # Create a connection
        conn = http.client.HTTPSConnection("api.musicapi.ai")
        
        # Prepare the payload
        payload = json.dumps({
            "name": "test persona",
            "description": "Pop, rap, rhythmic male bass",
            "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
        })
        
        # Prepare the headers - adding the Authorization header
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Make the request
        print("\nSending request to create persona...")
        conn.request("POST", "/api/v1/sonic/persona", payload, headers)
        
        # Get the response
        res = conn.getresponse()
        data = res.read()
        
        # Print the response
        print(f"\nResponse status: {res.status}")
        print(f"Response data: {data.decode('utf-8')}")
        
        return data.decode("utf-8")
    
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