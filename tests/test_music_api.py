"""
Tests for the MusicAPI integration.
"""
import unittest
import asyncio
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.music_api import MusicAPI

class TestMusicAPI(unittest.TestCase):
    """Test cases for the MusicAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.music_api = MusicAPI()
        
        # Sample data for testing
        self.persona_data = {
            "name": "Test Persona",
            "description": "A test persona for unit testing"
        }
        
        self.song_data = {
            "persona_id": "test-persona-id",
            "prompt": "Create a test song",
            "style": "kpop",
            "parameters": {
                "tempo": 120,
                "duration": 180
            }
        }
    
    def test_init_without_api_key(self):
        """Test initialization without an API key."""
        # Temporarily clear the API key
        with patch.dict('os.environ', {'MUSICAPI_KEY': ''}):
            api = MusicAPI()
            self.assertIsNone(api.api_key)
    
    @patch('httpx.AsyncClient.post')
    async def test_create_persona_with_mock(self, mock_post):
        """Test create_persona with a mocked HTTP client."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-persona-id",
            "name": self.persona_data["name"]
        }
        mock_post.return_value = mock_response
        
        # Set the API key
        self.music_api.api_key = "test_key"
        
        # Run the test
        result = await self.music_api.create_persona(
            name=self.persona_data["name"],
            description=self.persona_data["description"]
        )
        
        # Verify the result
        self.assertEqual(result["id"], "test-persona-id")
        self.assertEqual(result["name"], self.persona_data["name"])
        mock_post.assert_called_once()
    
    async def test_create_persona_without_api_key(self):
        """Test create_persona without an API key."""
        # Ensure there's no API key
        self.music_api.api_key = None
        
        # Run the test
        result = await self.music_api.create_persona(
            name=self.persona_data["name"],
            description=self.persona_data["description"]
        )
        
        # Verify we get a simulated response
        self.assertIn("id", result)
        self.assertEqual(result["name"], self.persona_data["name"])
    
    @patch('httpx.AsyncClient.post')
    async def test_create_song_with_mock(self, mock_post):
        """Test create_song with a mocked HTTP client."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-song-id",
            "audio_url": "https://example.com/test-song.mp3",
            "lyrics": "Test lyrics"
        }
        mock_post.return_value = mock_response
        
        # Set the API key
        self.music_api.api_key = "test_key"
        
        # Run the test
        result = await self.music_api.create_song(
            persona_id=self.song_data["persona_id"],
            prompt=self.song_data["prompt"],
            style=self.song_data["style"],
            parameters=self.song_data["parameters"]
        )
        
        # Verify the result
        self.assertEqual(result["id"], "test-song-id")
        self.assertEqual(result["audio_url"], "https://example.com/test-song.mp3")
        self.assertEqual(result["lyrics"], "Test lyrics")
        mock_post.assert_called_once()
    
    async def test_create_song_without_api_key(self):
        """Test create_song without an API key."""
        # Ensure there's no API key
        self.music_api.api_key = None
        
        # Run the test
        result = await self.music_api.create_song(
            persona_id=self.song_data["persona_id"],
            prompt=self.song_data["prompt"],
            style=self.song_data["style"],
            parameters=self.song_data["parameters"]
        )
        
        # Verify we get a simulated response
        self.assertIn("id", result)
        self.assertIn("audio_url", result)
        self.assertIn("lyrics", result)

def run_async_test(test_case):
    """Helper function to run async test cases."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_case)

if __name__ == '__main__':
    # Patch the TestCase to run async tests
    original_run = unittest.TestCase.run
    
    def run_with_async(self, result=None):
        """Run the test case, handling async methods."""
        if result is None:
            result = self.defaultTestResult()
        
        for method_name in dir(self):
            if method_name.startswith('test_') and asyncio.iscoroutinefunction(getattr(self, method_name)):
                setattr(self, method_name, lambda m=method_name: run_async_test(getattr(self.__class__, m)(self)))
        
        return original_run(self, result)
    
    unittest.TestCase.run = run_with_async
    
    unittest.main() 