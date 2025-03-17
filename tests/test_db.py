"""
Tests for the database integration.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import Database

class TestDatabase(unittest.TestCase):
    """Test cases for the Database class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = Database()
        
        # Sample data for testing
        self.song_data = {
            "title": "Test Song",
            "persona_id": "test-persona-id",
            "lyrics": "Test lyrics",
            "audio_url": "https://example.com/test-song.mp3",
            "params_used": {
                "prompt": "Create a test song",
                "style": "kpop"
            }
        }
    
    def test_init_without_credentials(self):
        """Test initialization without Supabase credentials."""
        # Temporarily clear the credentials
        with patch.dict('os.environ', {'SUPABASE_URL': '', 'SUPABASE_KEY': ''}):
            db = Database()
            self.assertIsNone(db.client)
    
    @patch('src.db.create_client')
    def test_init_with_credentials(self, mock_create_client):
        """Test initialization with Supabase credentials."""
        # Set up the mock
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Temporarily set the credentials
        with patch.dict('os.environ', {'SUPABASE_URL': 'test-url', 'SUPABASE_KEY': 'test-key'}):
            db = Database()
            self.assertIsNotNone(db.client)
            mock_create_client.assert_called_once_with('test-url', 'test-key')
    
    @patch('src.db.create_client')
    def test_store_song_with_client(self, mock_create_client):
        """Test store_song with a Supabase client."""
        # Set up the mock
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        
        mock_execute.return_value = {"data": [{"id": "test-id"}]}
        mock_insert.return_value = mock_execute
        mock_table.return_value = mock_insert
        mock_client.table = mock_table
        
        mock_create_client.return_value = mock_client
        
        # Temporarily set the credentials
        with patch.dict('os.environ', {'SUPABASE_URL': 'test-url', 'SUPABASE_KEY': 'test-key'}):
            db = Database()
            
            # Run the test
            result = db.store_song(
                title=self.song_data["title"],
                persona_id=self.song_data["persona_id"],
                lyrics=self.song_data["lyrics"],
                audio_url=self.song_data["audio_url"],
                params_used=self.song_data["params_used"]
            )
            
            # Verify the result
            mock_table.assert_called_once_with("songs")
            mock_insert.assert_called_once()
            mock_execute.assert_called_once()
    
    def test_store_song_without_client(self):
        """Test store_song without a Supabase client."""
        # Ensure there's no client
        self.db.client = None
        
        # Run the test
        result = self.db.store_song(
            title=self.song_data["title"],
            persona_id=self.song_data["persona_id"],
            lyrics=self.song_data["lyrics"],
            audio_url=self.song_data["audio_url"],
            params_used=self.song_data["params_used"]
        )
        
        # Verify we get a simulated response
        self.assertIn("id", result)
        self.assertEqual(result["title"], self.song_data["title"])
        self.assertEqual(result["persona_id"], self.song_data["persona_id"])
    
    @patch('src.db.create_client')
    def test_get_songs_with_client(self, mock_create_client):
        """Test get_songs with a Supabase client."""
        # Set up the mock
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_limit = MagicMock()
        mock_execute = MagicMock()
        
        mock_execute.return_value.data = [{"id": "test-id", "title": "Test Song"}]
        mock_limit.return_value = mock_execute
        mock_select.return_value = mock_limit
        mock_table.return_value = mock_select
        mock_client.table = mock_table
        
        mock_create_client.return_value = mock_client
        
        # Temporarily set the credentials
        with patch.dict('os.environ', {'SUPABASE_URL': 'test-url', 'SUPABASE_KEY': 'test-key'}):
            db = Database()
            
            # Run the test
            result = db.get_songs(limit=5)
            
            # Verify the result
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["id"], "test-id")
            self.assertEqual(result[0]["title"], "Test Song")
            
            mock_table.assert_called_once_with("songs")
            mock_select.assert_called_once_with("*")
            mock_limit.assert_called_once_with(5)
            mock_execute.assert_called_once()
    
    def test_get_songs_without_client(self):
        """Test get_songs without a Supabase client."""
        # Ensure there's no client
        self.db.client = None
        
        # Run the test
        result = self.db.get_songs(limit=5)
        
        # Verify we get a simulated response
        self.assertEqual(len(result), 1)
        self.assertIn("id", result[0])
        self.assertIn("title", result[0])

if __name__ == '__main__':
    unittest.main() 