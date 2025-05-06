#!/usr/bin/env python
"""
Yona CrewAI Tasks

This module defines the CrewAI Tasks that Yona will perform.
"""
import logging
from crewai import Task
from yona_crew_agent import create_yona_agent

logger = logging.getLogger(__name__)

def create_yona_tasks() -> list:
    """
    Create CrewAI Tasks for Yona
    
    Returns:
        List of CrewAI Task objects
    """
    logger.info("Creating Yona CrewAI Tasks")
    
    # Get the Yona agent
    yona_agent = create_yona_agent()
    
    # Create the tasks
    tasks = [
        Task(
            description='Generate and produce a song given a specific prompt.',
            agent=yona_agent,
            expected_output='Completed song metadata including audio, video, and image URLs.',
            context=[
                "Use the generate_song tool to create a new song based on the user's prompt.",
                "The tool will handle concept generation, lyrics creation, and song production.",
                "",
                "Example usage:",
                "```python",
                "song = generate_song(",
                "    prompt=\"Create a happy K-pop song about summer adventures\",",
                "    api=\"sonic\",  # or \"nuro\"",
                "    # Optional parameters:",
                "    style=\"kpop, upbeat, summer\",",
                "    negative_tags=\"sad, melancholic\",",
                "    make_instrumental=False,",
                "    mv=\"sonic-v4\",",
                "    description=\"A cheerful summer pop song with upbeat vibes\"",
                ")",
                "```",
                "",
                "For Nuro API, you can also specify:",
                "- gender: \"Female\" or \"Male\"",
                "- genre: \"Pop\", \"Rock\", \"Hip Hop/Rap\", \"R&B/Soul\", \"Electronic\"",
                "- mood: \"Happy\", \"Dynamic/Energetic\", \"Sentimental/Melancholic/Lonely\", \"Chill\"",
                "- timbre: \"Powerful\", \"Sexy/Lazy\"",
                "- duration: 30-240 seconds",
                "",
                "Return the song metadata including URLs for the audio, video, and image."
            ]
        ),
        Task(
            description='Process user feedback to iteratively improve an existing song.',
            agent=yona_agent,
            expected_output='New song version metadata reflecting feedback improvements.',
            context=[
                "Use the process_feedback tool to create a new version of a song based on user feedback.",
                "You'll need the original song ID and the feedback ID.",
                "",
                "Example usage:",
                "```python",
                "new_song = process_feedback(",
                "    song_id=\"123e4567-e89b-12d3-a456-426614174000\",",
                "    feedback_id=\"123e4567-e89b-12d3-a456-426614174001\"",
                ")",
                "```",
                "",
                "The tool will:",
                "1. Retrieve the original song and feedback from the database",
                "2. Use OpenAI to modify the song parameters based on the feedback",
                "3. Create a new song with the modified parameters",
                "4. Store the new song in the database with references to the original song and feedback",
                "5. Update the feedback record to mark it as processed",
                "",
                "Return the new song metadata including URLs for the audio, video, and image."
            ]
        ),
        Task(
            description='List songs from the database.',
            agent=yona_agent,
            expected_output='List of songs with metadata.',
            context=[
                "Use the list_songs tool to retrieve songs from the database.",
                "",
                "Example usage:",
                "```python",
                "songs = list_songs(limit=10, offset=0)",
                "```",
                "",
                "The tool will return a list of dictionaries containing song data.",
                "You can format this data to present it to the user in a readable way."
            ]
        ),
        Task(
            description='Process a natural language request from the user.',
            agent=yona_agent,
            expected_output='Result of the processed request.',
            context=[
                "Use the process_user_request tool to handle natural language requests.",
                "",
                "Example usage:",
                "```python",
                "result = process_user_request(\"Create a song about friendship\")",
                "```",
                "",
                "The tool will:",
                "1. Analyze the request to determine the intent (create_song, list_songs, get_song)",
                "2. Extract parameters from the request",
                "3. Execute the appropriate action",
                "4. Return the result with a human-readable response",
                "",
                "This is useful for handling complex or ambiguous requests."
            ]
        )
    ]
    
    logger.info(f"Created {len(tasks)} CrewAI Tasks")
    return tasks
