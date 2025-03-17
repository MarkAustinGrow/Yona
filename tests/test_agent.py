"""
Tests for the Yona agent.
"""
import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import YonaAgent

class TestYonaAgent(unittest.TestCase):
    """Test cases for the YonaAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = YonaAgent()
        
        # Sample song concept for testing
        self.song_concept = {
            "title": "Test Song",
            "theme": "testing",
            "mood": "focused",
            "lyrics_concept": "A song about writing tests",
            "musical_elements": ["beats", "synths"]
        }
    
    @patch('src.agent.OpenAI')
    def test_generate_song_concept_with_mock(self, mock_openai):
        """Test generate_song_concept with a mocked OpenAI client."""
        # Set up the mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(self.song_concept)
        mock_client.chat.completions.create.return_value = mock_response
        
        # Set the OpenAI key and client
        self.agent.openai_key = "test_key"
        self.agent.client = mock_client
        
        # Run the test
        result = asyncio.run(self.agent.generate_song_concept("Create a test song"))
        
        # Verify the result
        self.assertEqual(result, self.song_concept)
        mock_client.chat.completions.create.assert_called_once()
    
    def test_generate_song_concept_without_client(self):
        """Test generate_song_concept without an OpenAI client."""
        # Ensure there's no client
        self.agent.client = None
        
        # Run the test
        result = asyncio.run(self.agent.generate_song_concept("Create a test song"))
        
        # Verify we get a simulated response
        self.assertIn("title", result)
        self.assertIn("theme", result)
        self.assertIn("mood", result)
        self.assertIn("lyrics_concept", result)
        self.assertIn("musical_elements", result)
    
    @patch('src.agent.OpenAI')
    def test_generate_lyrics_with_mock(self, mock_openai):
        """Test generate_lyrics with a mocked OpenAI client."""
        # Set up the mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test lyrics"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Set the OpenAI key and client
        self.agent.openai_key = "test_key"
        self.agent.client = mock_client
        
        # Run the test
        result = asyncio.run(self.agent.generate_lyrics(self.song_concept))
        
        # Verify the result
        self.assertEqual(result, "Test lyrics")
        mock_client.chat.completions.create.assert_called_once()
    
    def test_generate_lyrics_without_client(self):
        """Test generate_lyrics without an OpenAI client."""
        # Ensure there's no client
        self.agent.client = None
        
        # Run the test
        result = asyncio.run(self.agent.generate_lyrics(self.song_concept))
        
        # Verify we get a simulated response
        self.assertTrue(isinstance(result, str))
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main() 