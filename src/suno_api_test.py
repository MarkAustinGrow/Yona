import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("MUSICAPI_KEY")

print("Testing Suno API endpoints...")
print(f"Using API key: {api_key}")

# List of potential Suno API endpoints
suno_endpoints = [
    "https://api.suno.ai",
    "https://api.suno.ai/api/v1",
    "https://api.suno.ai/v1",
    "https://suno.ai/api"
]

# Test headers with different authorization formats
auth_headers = [
    {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    {"Content-Type": "application/json", "Authorization": api_key},
    {"Content-Type": "application/json", "x-api-key": api_key}
]

# Test each endpoint with GET request
print("\n=== Testing GET requests to Suno endpoints ===")
for endpoint in suno_endpoints:
    try:
        print(f"\nTesting GET to {endpoint}")
        # First try without auth
        response = requests.get(endpoint, timeout=10)
        print(f"Status (no auth): {response.status_code}")
        print(f"Response preview: {response.text[:100]}...")
        
        # Then try with auth
        response = requests.get(
            endpoint, 
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        print(f"Status (with auth): {response.status_code}")
        print(f"Response preview: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test specific Suno API endpoints for generating music
print("\n=== Testing Suno API specific endpoints ===")

# Potential Suno API endpoints for generating music
generation_endpoints = [
    "https://api.suno.ai/api/v1/generate",
    "https://api.suno.ai/v1/generate",
    "https://api.suno.ai/generate"
]

# Simple generation payload
generation_payload = {
    "prompt": "Energetic K-pop track about friendship and summer fun",
    "style": "kpop",
    "tempo": 120,
    "duration": 30
}

# Test each generation endpoint
for endpoint in generation_endpoints:
    for i, headers in enumerate(auth_headers):
        try:
            print(f"\nTesting POST to {endpoint} with headers set {i+1}")
            response = requests.post(
                endpoint,
                json=generation_payload,
                headers=headers,
                timeout=10
            )
            print(f"Status: {response.status_code}")
            print(f"Response preview: {response.text[:100]}...")
        except Exception as e:
            print(f"Error: {str(e)}")

print("\nSuno API testing complete.") 