import http.client
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("MUSICAPI_KEY")

print("Testing API key validity using exact format from Roadmap.md...")
print(f"Using API key: {api_key}")

# Test persona creation using the exact code from Roadmap.md
print("\n=== Testing persona creation using http.client (from Roadmap.md) ===")
try:
    conn = http.client.HTTPSConnection("api.musicapi.ai")
    payload = json.dumps({
        "name": "Yona",
        "description": "Energetic K-pop idol persona with bright EDM influences, occasionally rapping segments.",
        "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
    })
    
    # First try without auth header (as shown in Roadmap.md)
    headers = {'Content-Type': 'application/json'}
    print("\nTesting without Authorization header...")
    conn.request("POST", "/api/v1/sonic/persona", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(f"Status: {res.status}")
    print(f"Response: {data.decode('utf-8')[:100]}...")
    
    # Then try with auth header
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    print("\nTesting with Authorization header...")
    conn.request("POST", "/api/v1/sonic/persona", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(f"Status: {res.status}")
    print(f"Response: {data.decode('utf-8')[:100]}...")
    
except Exception as e:
    print(f"Error: {str(e)}")

# Test song creation using the exact code from Roadmap.md
print("\n=== Testing song creation using http.client (from Roadmap.md) ===")
try:
    conn = http.client.HTTPSConnection("api.musicapi.ai")
    create_song_payload = {
        "persona_id": "test_persona_id",  # We don't have a real persona ID yet
        "prompt": "Compose an energetic K-pop track about friendship and summer fun",
        "style": "kpop",
        "parameters": {
            "tempo": 120,
            "duration": 180
        }
    }
    payload = json.dumps(create_song_payload)
    
    # First try without auth header (as shown in Roadmap.md)
    headers = {'Content-Type': 'application/json'}
    print("\nTesting without Authorization header...")
    conn.request("POST", "/api/v1/sonic/music", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(f"Status: {res.status}")
    print(f"Response: {data.decode('utf-8')[:100]}...")
    
    # Then try with auth header
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    print("\nTesting with Authorization header...")
    conn.request("POST", "/api/v1/sonic/music", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(f"Status: {res.status}")
    print(f"Response: {data.decode('utf-8')[:100]}...")
    
except Exception as e:
    print(f"Error: {str(e)}")

print("\nAPI key validation testing complete.") 