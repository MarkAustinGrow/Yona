"""
Test script that checks if the MusicAPI.ai API is accessible.
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_status():
    """Test if the MusicAPI.ai API is accessible."""
    print("Testing if the MusicAPI.ai API is accessible...")
    
    # Get the API key
    api_key = os.getenv("MUSICAPI_KEY")
    if not api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    try:
        # Try a simple GET request to the API root
        url = "https://api.musicapi.ai/"
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        print("\nSending GET request to API root...")
        response = requests.get(url, headers=headers)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response text: {response.text[:500]}...")  # Print first 500 chars
        
        # Try a GET request to the /api/v1 endpoint
        url = "https://api.musicapi.ai/api/v1"
        
        print("\nSending GET request to /api/v1 endpoint...")
        response = requests.get(url, headers=headers)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response text: {response.text[:500]}...")  # Print first 500 chars
        
        # Try a GET request to the /api/v1/sonic endpoint
        url = "https://api.musicapi.ai/api/v1/sonic"
        
        print("\nSending GET request to /api/v1/sonic endpoint...")
        response = requests.get(url, headers=headers)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response text: {response.text[:500]}...")  # Print first 500 chars
        
        return True
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the test
    result = test_api_status()
    
    if result:
        print("\nAPI is accessible!")
    else:
        print("\nAPI is not accessible.") 