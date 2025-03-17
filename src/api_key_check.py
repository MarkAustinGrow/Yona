import requests
import os
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("MUSICAPI_KEY")

print("Checking MusicAPI.ai API key status...")
print(f"Using API key: {api_key}")

# Persona creation endpoint
persona_endpoint = "https://api.musicapi.ai/api/v1/sonic/persona"

# Persona creation payload
persona_payload = {
    "name": "Yona",
    "description": "Energetic K-pop idol persona with bright EDM influences, occasionally rapping segments.",
    "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
}

# Headers with Bearer token (double space format that gave us the key error)
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer  {api_key}"
}

# Make the request
print("\nSending request to check API key status...")
try:
    response = requests.post(
        persona_endpoint,
        json=persona_payload,
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Check for specific error messages
    if response.status_code == 401:
        error_text = response.text.lower()
        if "incorrect" in error_text:
            print("\nAPI KEY STATUS: INVALID - The API key is incorrect")
        elif "expired" in error_text:
            print("\nAPI KEY STATUS: EXPIRED - The API key has expired")
        elif "unauthorized" in error_text:
            print("\nAPI KEY STATUS: UNAUTHORIZED - The API key is not authorized")
        else:
            print(f"\nAPI KEY STATUS: UNKNOWN ERROR - {response.text}")
    elif response.status_code == 500:
        print("\nAPI KEY STATUS: SERVER ERROR - The server returned an internal error")
    elif response.status_code == 200:
        print("\nAPI KEY STATUS: VALID - The API key is valid and working")
    else:
        print(f"\nAPI KEY STATUS: UNKNOWN - Unexpected status code {response.status_code}")
        
except Exception as e:
    print(f"Error: {str(e)}")

# Try to get information about the API key
print("\nAttempting to get API key information...")
try:
    # Common endpoints for API key info
    key_endpoints = [
        "https://api.musicapi.ai/api/v1/account",
        "https://api.musicapi.ai/api/v1/user",
        "https://api.musicapi.ai/api/v1/key",
        "https://api.musicapi.ai/api/v1/auth/verify"
    ]
    
    for endpoint in key_endpoints:
        print(f"\nChecking {endpoint}...")
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}...")
        
        # If we get a successful response, no need to check other endpoints
        if response.status_code == 200:
            break
            
except Exception as e:
    print(f"Error: {str(e)}")

print("\nAPI key check complete.") 