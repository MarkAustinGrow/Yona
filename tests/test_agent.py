#!/usr/bin/env python
"""
Tests for the YonaAgent class.

This module contains unit tests for the YonaAgent class, which is the brain of Yona,
an agentic AI K-pop star.
"""
import unittest
import json
from unittest.mock import patch, MagicMock

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import YonaAgent


class TestYonaAgent(unittest.TestCase):
    """Test cases for the YonaAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a YonaAgent instance in simulation mode for testing
        self.agent = YonaAgent(simulation_mode=True)

    def test_initialization(self):
        """Test that the YonaAgent initializes correctly."""
        self.assertTrue(self.agent.simulation_mode)
        self.assertIsNotNone(self.agent.music_api)
        self.assertIsNotNone(self.agent.supabase_client)
        self.assertIsNotNone(self.agent.persona)

    def test_generate_song_concept(self):
        """Test generating a song concept."""
        prompt = "Create a song about friendship"
        concept = self.agent.generate_song_concept(prompt)
        
        # Check that the concept has the expected keys
        self.assertIn("title", concept)
        self.assertIn("theme", concept)
        self.assertIn("mood", concept)
        self.assertIn("musical_elements", concept)
        self.assertIn("lyrics_concept", concept)

    def test_generate_lyrics(self):
        """Test generating lyrics from a concept."""
        concept = {
            "title": "Test Song",
            "theme": "Testing",
            "mood": "Determined",
            "musical_elements": "Electronic",
            "lyrics_concept": "A song about writing tests"
        }
        
        lyrics = self.agent.generate_lyrics(concept)
        
        # Check that lyrics were generated
        self.assertIsNotNone(lyrics)
        self.assertIsInstance(lyrics, str)
        self.assertGreater(len(lyrics), 0)

    def test_create_song(self):
        """Test creating a song."""
        title = "Test Song"
        lyrics = "Test lyrics for a test song"
        
        result = self.agent.create_song(title, lyrics)
        
        # Check that the result has the expected keys
        self.assertIn("title", result)
        self.assertIn("audio_url", result)
        self.assertIn("video_url", result)
        self.assertIn("image_url", result)
        self.assertIn("status", result)
        
        # Check that the status is succeeded
        self.assertEqual(result["status"], "succeeded")

    def test_list_songs(self):
        """Test listing songs."""
        songs = self.agent.list_songs()
        
        # Check that songs is a list
        self.assertIsInstance(songs, list)
        
        # Check that each song has the expected keys
        for song in songs:
            self.assertIn("id", song)
            self.assertIn("title", song)
            self.assertIn("audio_url", song)

    def test_process_user_request_simulation(self):
        """Test processing a user request in simulation mode."""
        user_input = "Create a song about the ocean"
        result = self.agent.process_user_request(user_input)
        
        # Check that the result has the expected keys
        self.assertIn("action", result)
        self.assertIn("result", result)
        self.assertIn("response", result)

    @patch('src.agent.YonaAgent._analyze_request')
    def test_process_user_request_create_song(self, mock_analyze_request):
        """Test processing a create song request."""
        # Mock the _analyze_request method to return a create_song intent
        mock_analyze_request.return_value = {
            "intent": "create_song",
            "parameters": {
                "prompt": "Create a song about the ocean"
            }
        }
        
        # Mock the generate_song_concept method
        with patch.object(self.agent, 'generate_song_concept') as mock_generate_concept:
            mock_generate_concept.return_value = {
                "title": "Ocean Waves",
                "theme": "Ocean",
                "mood": "Calm",
                "musical_elements": "Ambient",
                "lyrics_concept": "A song about the calming waves of the ocean"
            }
            
            # Mock the generate_lyrics method
            with patch.object(self.agent, 'generate_lyrics') as mock_generate_lyrics:
                mock_generate_lyrics.return_value = "Test lyrics about the ocean"
                
                # Mock the create_song method
                with patch.object(self.agent, 'create_song') as mock_create_song:
                    mock_create_song.return_value = {
                        "title": "Ocean Waves",
                        "audio_url": "https://example.com/audio.mp3",
                        "video_url": "https://example.com/video.mp4",
                        "image_url": "https://example.com/image.jpg",
                        "status": "succeeded"
                    }
                    
                    # Process the request
                    user_input = "Create a song about the ocean"
                    result = self.agent.process_user_request(user_input)
                    
                    # Check that the result has the expected keys
                    self.assertIn("action", result)
                    self.assertIn("result", result)
                    self.assertIn("response", result)
                    
                    # Check that the action is create_song
                    self.assertEqual(result["action"], "create_song")
                    
                    # Check that the methods were called with the expected arguments
                    mock_analyze_request.assert_called_once_with(user_input)
                    mock_generate_concept.assert_called_once_with("Create a song about the ocean")
                    mock_generate_lyrics.assert_called_once()
                    mock_create_song.assert_called_once_with(
                        title="Ocean Waves",
                        lyrics="Test lyrics about the ocean",
                        style=None,
                        negative_tags=None,
                        make_instrumental=False,
                        mv='sonic-v4',
                        gpt_description_prompt=None,
                        voice_gender='female'
                    )

    @patch('src.agent.YonaAgent._analyze_request')
    def test_process_user_request_list_songs(self, mock_analyze_request):
        """Test processing a list songs request."""
        # Mock the _analyze_request method to return a list_songs intent
        mock_analyze_request.return_value = {
            "intent": "list_songs",
            "parameters": {
                "limit": 5
            }
        }
        
        # Mock the list_songs method
        with patch.object(self.agent, 'list_songs') as mock_list_songs:
            mock_list_songs.return_value = [
                {
                    "id": "1",
                    "title": "Song 1",
                    "audio_url": "https://example.com/song1.mp3"
                },
                {
                    "id": "2",
                    "title": "Song 2",
                    "audio_url": "https://example.com/song2.mp3"
                }
            ]
            
            # Process the request
            user_input = "List my songs"
            result = self.agent.process_user_request(user_input)
            
            # Check that the result has the expected keys
            self.assertIn("action", result)
            self.assertIn("result", result)
            self.assertIn("response", result)
            
            # Check that the action is list_songs
            self.assertEqual(result["action"], "list_songs")
            
            # Check that the methods were called with the expected arguments
            mock_analyze_request.assert_called_once_with(user_input)
            mock_list_songs.assert_called_once_with(limit=5, offset=0)

    @patch('src.agent.YonaAgent._analyze_request')
    def test_process_user_request_get_song(self, mock_analyze_request):
        """Test processing a get song request."""
        # Mock the _analyze_request method to return a get_song intent
        mock_analyze_request.return_value = {
            "intent": "get_song",
            "parameters": {
                "song_id": "123"
            }
        }
        
        # Mock the get_song_by_id method of supabase_client
        with patch.object(self.agent.supabase_client, 'get_song_by_id') as mock_get_song:
            mock_get_song.return_value = {
                "id": "123",
                "title": "Test Song",
                "audio_url": "https://example.com/test.mp3"
            }
            
            # Process the request
            user_input = "Get song 123"
            result = self.agent.process_user_request(user_input)
            
            # Check that the result has the expected keys
            self.assertIn("action", result)
            self.assertIn("result", result)
            self.assertIn("response", result)
            
            # Check that the action is get_song
            self.assertEqual(result["action"], "get_song")
            
            # Check that the methods were called with the expected arguments
            mock_analyze_request.assert_called_once_with(user_input)
            mock_get_song.assert_called_once_with("123")

    @patch('src.agent.YonaAgent._analyze_request')
    def test_process_user_request_unknown_intent(self, mock_analyze_request):
        """Test processing a request with an unknown intent."""
        # Mock the _analyze_request method to return an unknown intent
        mock_analyze_request.return_value = {
            "intent": "unknown",
            "parameters": {}
        }
        
        # Process the request
        user_input = "Do something else"
        result = self.agent.process_user_request(user_input)
        
        # Check that the result has the expected keys
        self.assertIn("action", result)
        self.assertIn("result", result)
        self.assertIn("response", result)
        
        # Check that the action is unknown
        self.assertEqual(result["action"], "unknown")
        
        # Check that the methods were called with the expected arguments
        mock_analyze_request.assert_called_once_with(user_input)


if __name__ == '__main__':
    unittest.main()
