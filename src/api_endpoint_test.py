import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("MUSICAPI_KEY")

print("Testing different MusicAPI.ai endpoint structures...")
print(f"Using API key: {api_key}")

# List of potential endpoints to test
endpoints = [
    # Base endpoints
    "https://api.musicapi.ai",
    "https://musicapi.ai/api",
    "https://www.musicapi.ai/api",
    
    # Persona endpoints from Roadmap.md
    "https://api.musicapi.ai/api/v1/sonic/persona",
    "https://musicapi.ai/api/v1/sonic/persona",
    
    # Music endpoints from Roadmap.md
    "https://api.musicapi.ai/api/v1/sonic/music",
    "https://musicapi.ai/api/v1/sonic/music"
]

# Test headers with different authorization formats
auth_headers = [
    {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    {"Content-Type": "application/json", "Authorization": api_key},
    {"Content-Type": "application/json", "x-api-key": api_key},
    {"Content-Type": "application/json"}  # No auth header as a baseline
]

# Persona creation payload from Roadmap.md
persona_payload = {
    "name": "Yona",
    "description": "Energetic K-pop idol persona with bright EDM influences, occasionally rapping segments.",
    "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
}

# Test each endpoint with GET request first
print("\n=== Testing GET requests to endpoints ===")
for endpoint in endpoints:
    try:
        print(f"\nTesting GET to {endpoint}")
        response = requests.get(endpoint, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response preview: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test persona creation with different auth headers
print("\n=== Testing POST requests for persona creation ===")
persona_endpoint = "https://api.musicapi.ai/api/v1/sonic/persona"

for i, headers in enumerate(auth_headers):
    try:
        print(f"\nTest {i+1}: Using headers: {json.dumps(headers)}")
        response = requests.post(
            persona_endpoint,
            json=persona_payload,
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response preview: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

print("\nEndpoint testing complete.") 