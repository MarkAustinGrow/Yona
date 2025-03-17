import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("MUSICAPI_KEY")

print("Testing different Bearer token formats...")
print(f"Using API key: {api_key}")

# Persona creation endpoint
persona_endpoint = "https://api.musicapi.ai/api/v1/sonic/persona"

# Persona creation payload
persona_payload = {
    "name": "Yona",
    "description": "Energetic K-pop idol persona with bright EDM influences, occasionally rapping segments.",
    "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
}

# Different Bearer token formats to test
bearer_formats = [
    f"Bearer {api_key}",
    f"bearer {api_key}",
    f"BEARER {api_key}",
    f"Bearer  {api_key}",  # Double space
    f"Bearer{api_key}",    # No space
    api_key,               # No Bearer prefix
    f"Token {api_key}",    # Different prefix
    f"Basic {api_key}"     # Different prefix
]

# Test each Bearer format
print("\n=== Testing different Bearer token formats ===")
for i, bearer_format in enumerate(bearer_formats):
    try:
        print(f"\nTest {i+1}: Using Authorization: {bearer_format}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": bearer_format
        }
        response = requests.post(
            persona_endpoint,
            json=persona_payload,
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

# Try with different content types
content_types = [
    "application/json",
    "application/x-www-form-urlencoded",
    "multipart/form-data"
]

print("\n=== Testing different Content-Type headers ===")
for i, content_type in enumerate(content_types):
    try:
        print(f"\nTest {i+1}: Using Content-Type: {content_type}")
        headers = {
            "Content-Type": content_type,
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.post(
            persona_endpoint,
            json=persona_payload,
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

print("\nBearer format testing complete.") 