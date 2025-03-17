"""
Yona agent implementation using ChatGPT as the brain.
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from config.config import OPENAI_KEY, OPENAI_MODEL, YONA_PERSONA

load_dotenv()

class YonaAgent:
    """
    Yona agent class that uses ChatGPT as its brain for decision-making.
    """
    
    def __init__(self):
        """Initialize the Yona agent."""
        self.openai_key = OPENAI_KEY
        self.model = OPENAI_MODEL
        
        if not self.openai_key:
            print("Warning: OpenAI API key not found. Agent operations will be simulated.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.openai_key)
        
        # Define Yona's persona from config
        self.persona = YONA_PERSONA
    
    async def generate_song_concept(self, user_prompt):
        """
        Generate a song concept based on user input.
        
        Args:
            user_prompt (str): The user's prompt for song creation
        
        Returns:
            dict: A structured song concept
        """
        if not self.client:
            # Simulate a response
            print(f"Simulated: Generated song concept from prompt '{user_prompt}'")
            return {
                "title": "Simulated Song Title",
                "theme": "love and friendship",
                "mood": "upbeat",
                "lyrics_concept": "A song about supporting friends through difficult times",
                "musical_elements": ["EDM beats", "bright synths", "rap bridge"]
            }
        
        # Create a system message that defines Yona's role
        system_message = f"""
        You are Yona, a K-pop star AI agent. Your task is to create a song concept based on the user's prompt.
        Your personality: {', '.join(self.persona['personality_traits'])}
        Your musical style: {self.persona['style']} with {self.persona['description']}
        
        Generate a structured song concept with the following elements:
        - title: A catchy title for the song
        - theme: The main theme or topic
        - mood: The emotional mood of the song
        - lyrics_concept: A brief description of what the lyrics should convey
        - musical_elements: A list of musical elements to include
        
        Format your response as a JSON object.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        concept = json.loads(response.choices[0].message.content)
        return concept
    
    async def generate_lyrics(self, song_concept):
        """
        Generate lyrics based on a song concept.
        
        Args:
            song_concept (dict): The song concept
        
        Returns:
            str: The generated lyrics
        """
        if not self.client:
            # Simulate a response
            print(f"Simulated: Generated lyrics for song concept '{song_concept['title']}'")
            return "Simulated lyrics for the song\nVerse 1: ...\nChorus: ...\nVerse 2: ...\nBridge: ...\nChorus: ..."
        
        # Create a system message for lyrics generation
        system_message = f"""
        You are Yona, a K-pop star AI agent. Your task is to write lyrics for a song based on the provided concept.
        Your personality: {', '.join(self.persona['personality_traits'])}
        Your musical style: {self.persona['style']} with {self.persona['description']}
        
        Write lyrics for a K-pop song with the following structure:
        - Verse 1
        - Pre-Chorus
        - Chorus
        - Verse 2
        - Pre-Chorus
        - Chorus
        - Bridge (with rap elements)
        - Final Chorus
        
        The lyrics should match the theme, mood, and concept provided.
        """
        
        # Format the song concept as a prompt
        user_prompt = f"""
        Song Title: {song_concept['title']}
        Theme: {song_concept['theme']}
        Mood: {song_concept['mood']}
        Lyrics Concept: {song_concept['lyrics_concept']}
        Musical Elements: {', '.join(song_concept['musical_elements'])}
        
        Please write the complete lyrics for this song.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Get the lyrics from the response
        lyrics = response.choices[0].message.content
        return lyrics
    
    async def generate_music_prompt(self, song_concept, lyrics):
        """
        Generate a prompt for MusicAPI.ai based on the song concept and lyrics.
        
        Args:
            song_concept (dict): The song concept
            lyrics (str): The generated lyrics
        
        Returns:
            dict: A structured prompt for MusicAPI.ai
        """
        if not self.client:
            # Simulate a response
            print(f"Simulated: Generated music prompt for song '{song_concept['title']}'")
            return {
                "prompt": f"Create an energetic K-pop song titled '{song_concept['title']}' about {song_concept['theme']}",
                "style": "kpop",
                "parameters": {
                    "tempo": 120,
                    "duration": 180
                }
            }
        
        # Create a system message for music prompt generation
        system_message = f"""
        You are Yona, a K-pop star AI agent. Your task is to create a prompt for MusicAPI.ai to generate music.
        Your personality: {', '.join(self.persona['personality_traits'])}
        Your musical style: {self.persona['style']} with {self.persona['description']}
        
        Based on the song concept and lyrics, create a detailed prompt for MusicAPI.ai.
        The prompt should include:
        - A clear description of the desired musical style and elements
        - References to the mood and theme
        - Specific musical elements to include (e.g., EDM beats, synths, etc.)
        
        Also determine appropriate parameters:
        - tempo: The tempo of the song in BPM
        - duration: The duration of the song in seconds
        
        Format your response as a JSON object with the following structure:
        {
            "prompt": "The detailed prompt for MusicAPI.ai",
            "style": "The style of the song (e.g., kpop)",
            "parameters": {
                "tempo": 120,
                "duration": 180
            }
        }
        """
        
        # Format the song concept and lyrics as a prompt
        user_prompt = f"""
        Song Title: {song_concept['title']}
        Theme: {song_concept['theme']}
        Mood: {song_concept['mood']}
        Musical Elements: {', '.join(song_concept['musical_elements'])}
        
        Lyrics:
        {lyrics[:500]}... (truncated for brevity)
        
        Please create a detailed prompt for MusicAPI.ai to generate this song.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        music_prompt = json.loads(response.choices[0].message.content)
        return music_prompt 