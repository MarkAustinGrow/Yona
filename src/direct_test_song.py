"""
Direct test script for creating a song on MusicAPI.ai using the exact code from the documentation.
"""
import http.client
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_song_creation(persona_id):
    """
    Test creating a song using the exact code from the documentation.
    
    Args:
        persona_id (str): The ID of the persona to use.
    """
    print("Testing song creation on MusicAPI.ai using direct HTTP request...")
    
    # Get the API key
    api_key = os.getenv("MUSICAPI_KEY")
    if not api_key:
        print("Error: No MusicAPI key found. Please check your .env file.")
        return
    
    if not persona_id:
        print("Error: No persona ID provided.")
        return
    
    try:
        # Create a connection
        conn = http.client.HTTPSConnection("api.musicapi.ai")
        
        # Sample lyrics for testing
        lyrics = """
        [Verse]
        Stars they shine above me
        Moonlight softly glows
        Whispers in the night sky
        Dreams that only grow

        [Verse 2]
        Midnight winds are calling
        Carrying a tune
        Heartbeats echo softly
        Dancing with the moon

        [Chorus]
        Starry night starry night
        Let your light ignite ignite
        Bright as day bright as day
        Guide my way guide my way

        [Verse 3]
        Shadows move and twinkle
        Nighttime come alive
        Mystery in the heavens
        Stories that survive

        [Bridge]
        Magic fills the darkness
        Wonder in the air
        Every star a secret
        In the sky I stare

        [Chorus]
        Starry night starry night
        Let your light ignite ignite
        Bright as day bright as day
        Guide my way guide my way
        """
        
        # Prepare the payload
        payload = json.dumps({
            "task_type": "persona_music",
            "custom_mode": True,
            "prompt": lyrics,
            "title": "Starry Night",
            "tags": "kpop",
            "persona_id": persona_id,
            "mv": "sonic-v3-5"
        })
        
        # Prepare the headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Make the request to create the song
        print("\nSending request to create song...")
        conn.request("POST", "/api/v1/sonic/create", payload, headers)
        
        # Get the response
        res = conn.getresponse()
        data = res.read()
        
        # Print the response
        print(f"\nResponse status: {res.status}")
        print(f"Response data: {data.decode('utf-8')}")
        
        # Parse the response
        if res.status == 200:
            response_data = json.loads(data.decode('utf-8'))
            task_id = response_data.get('task_id')
            print(f"\nSong creation task started with ID: {task_id}")
            
            # Poll for the result
            print("\nPolling for the result...")
            max_attempts = 30
            for attempt in range(max_attempts):
                print(f"Attempt {attempt + 1}/{max_attempts}...")
                
                # Wait a bit before checking
                time.sleep(5)
                
                # Create a new connection for each request
                conn = http.client.HTTPSConnection("api.musicapi.ai")
                
                # Make the request to check the status
                conn.request("GET", f"/api/v1/sonic/music?task_id={task_id}", headers=headers)
                
                # Get the response
                status_res = conn.getresponse()
                status_data = status_res.read()
                
                # Print the response
                print(f"Status response: {status_res.status}")
                print(f"Status data: {status_data.decode('utf-8')}")
                
                # Parse the response
                if status_res.status == 200:
                    status_json = json.loads(status_data.decode('utf-8'))
                    status = status_json.get('status')
                    
                    if status == "success":
                        print("\nSong created successfully!")
                        print(f"Audio URL: {status_json.get('audio_url')}")
                        return status_json
                    elif status == "failed":
                        print(f"\nSong creation failed: {status_json.get('message')}")
                        return None
                    else:
                        print(f"Status: {status}. Continuing to poll...")
                else:
                    print(f"\nError checking status: {status_data.decode('utf-8')}")
                    return None
            
            print("\nTimed out waiting for song creation to complete.")
            return None
        else:
            print(f"\nError: Received status code {res.status}")
            return None
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        return None

if __name__ == "__main__":
    # Get persona ID from command line
    import sys
    if len(sys.argv) < 2:
        print("Error: Please provide a persona ID as a command line argument.")
        print("Usage: python direct_test_song.py <persona_id>")
        sys.exit(1)
    
    persona_id = sys.argv[1]
    
    # Run the test
    result = test_song_creation(persona_id)
    
    if result:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed.") 