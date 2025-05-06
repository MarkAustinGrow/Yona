# Integrating Yona AI Agent with CrewAI

This guide provides detailed instructions for integrating the Yona AI agent with CrewAI, ensuring proper connection to all Yona's capabilities including song generation, feedback processing, and DID/MCP functionality.

## Step 1: Environment Setup

Create a Python environment and install the dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install crewai openai supabase python-dotenv httpx flask cryptography
```

## Step 2: Securely Manage API Keys

Create a `.env` file with all required API keys:

```bash
OPENAI_KEY=your_openai_key
MUSICAPI_KEY=your_musicapi_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Create a configuration module to load these environment variables:

```python
# crew_config.py
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Keys
OPENAI_KEY = os.getenv('OPENAI_KEY')
MUSICAPI_KEY = os.getenv('MUSICAPI_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Validate required environment variables
if not all([OPENAI_KEY, MUSICAPI_KEY, SUPABASE_URL, SUPABASE_KEY]):
    missing = []
    if not OPENAI_KEY: missing.append("OPENAI_KEY")
    if not MUSICAPI_KEY: missing.append("MUSICAPI_KEY")
    if not SUPABASE_URL: missing.append("SUPABASE_URL")
    if not SUPABASE_KEY: missing.append("SUPABASE_KEY")
    logger.error(f"Missing required environment variables: {', '.join(missing)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

logger.info("Environment variables loaded successfully")
```

## Step 3: Initialize the Yona Implementation

Create a module to initialize and manage the Yona implementation:

```python
# yona_implementation.py
import logging
import json
from src.agent import YonaAgent
from crew_config import OPENAI_KEY

logger = logging.getLogger(__name__)

class YonaImplementationManager:
    """
    Manages the Yona implementation and provides methods to access its functionality.
    This class serves as a bridge between CrewAI and the Yona codebase.
    """
    
    def __init__(self, did_domain="yona.ai", private_key_path=None):
        """Initialize the Yona implementation manager"""
        logger.info("Initializing Yona Implementation Manager")
        
        try:
            # Initialize the actual Yona implementation
            self.yona = YonaAgent(
                openai_api_key=OPENAI_KEY,
                did_domain=did_domain,
                private_key_path=private_key_path
            )
            logger.info(f"Yona agent initialized with DID: {self.yona.did_manager.did}")
        except Exception as e:
            logger.error(f"Failed to initialize Yona agent: {str(e)}")
            raise
    
    def generate_song(self, prompt, api="sonic", **kwargs):
        """
        Generate a song based on a prompt
        
        Args:
            prompt: The prompt describing the song to create
            api: Which API to use ('sonic' or 'nuro')
            **kwargs: Additional parameters for song creation
            
        Returns:
            Dictionary containing the song data, including URLs and metadata
        """
        logger.info(f"Generating song from prompt: {prompt} using {api} API")
        
        try:
            # Generate song concept
            concept = self.yona.generate_song_concept(prompt)
            logger.info(f"Generated concept: {concept.get('title')}")
            
            # Generate lyrics
            lyrics = self.yona.generate_lyrics(concept)
            logger.info(f"Generated lyrics (excerpt): {lyrics[:50]}...")
            
            # Extract parameters from the concept
            title = concept.get('title')
            style = concept.get('style_tags')
            negative_tags = concept.get('negative_tags')
            make_instrumental = concept.get('make_instrumental', False)
            mv = concept.get('mv_type', 'sonic-v4')
            description = concept.get('description', '')
            
            # Override parameters if provided in kwargs
            title = kwargs.get('title', title)
            style = kwargs.get('style', style)
            negative_tags = kwargs.get('negative_tags', negative_tags)
            make_instrumental = kwargs.get('make_instrumental', make_instrumental)
            mv = kwargs.get('mv', mv)
            description = kwargs.get('description', description)
            
            # Create the song using the appropriate API
            if api == "nuro":
                # Extract Nuro-specific parameters
                gender = kwargs.get('gender', concept.get('gender', 'Female'))
                genre = kwargs.get('genre', concept.get('genre', 'Pop'))
                mood = kwargs.get('mood', concept.get('mood', 'Happy'))
                timbre = kwargs.get('timbre', concept.get('timbre', 'Powerful'))
                duration = kwargs.get('duration', concept.get('duration', 60))
                
                # Create song with Nuro API
                song = self.yona.create_song(
                    title=title,
                    lyrics=lyrics,
                    api='nuro',
                    gender=gender,
                    genre=genre,
                    mood=mood,
                    timbre=timbre,
                    duration=duration,
                    mv=mv
                )
            else:
                # Create song with Sonic API
                song = self.yona.create_song(
                    title=title,
                    lyrics=lyrics,
                    style=style,
                    negative_tags=negative_tags,
                    make_instrumental=make_instrumental,
                    mv=mv,
                    gpt_description_prompt=description,
                    voice_gender=kwargs.get('voice_gender', 'female')
                )
            
            # Add concept and lyrics to the result
            if song.get('status') != 'failed':
                song['concept'] = concept
                song['lyrics'] = lyrics
            
            return song
            
        except Exception as e:
            logger.error(f"Error generating song: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "prompt": prompt
            }
    
    def process_feedback(self, song_id, feedback_id):
        """
        Process feedback for a song
        
        Args:
            song_id: ID of the original song
            feedback_id: ID of the feedback to process
            
        Returns:
            Dictionary containing the new song data
        """
        logger.info(f"Processing feedback {feedback_id} for song {song_id}")
        
        try:
            # Get the original song
            original_song = self.yona.supabase_client.get_song_by_id(song_id)
            if not original_song:
                logger.error(f"Original song {song_id} not found")
                return {"status": "failed", "error": f"Original song {song_id} not found"}
            
            # Get the feedback
            feedback = self.yona.supabase_client.get_feedback_by_id(feedback_id)
            if not feedback:
                logger.error(f"Feedback {feedback_id} not found")
                return {"status": "failed", "error": f"Feedback {feedback_id} not found"}
            
            # Extract parameters from the original song
            original_params = original_song.get('params_used', {})
            if not original_params:
                logger.warning(f"No params_used found for song {song_id}, using defaults")
                original_params = {
                    'prompt': original_song.get('lyrics', ''),
                    'title': original_song.get('title', 'Untitled'),
                    'style': original_song.get('style', ''),
                    'negative_tags': original_song.get('negative_tags', ''),
                    'make_instrumental': original_song.get('make_instrumental', False),
                    'mv': original_song.get('mv', 'sonic-v4'),
                    'gpt_description_prompt': original_song.get('gpt_description', ''),
                    'voice_gender': 'female'
                }
            
            # Modify parameters based on feedback
            modified_params = self._modify_parameters_with_openai(original_params, feedback.get('comments', ''))
            
            # Create a new song with the modified parameters
            api_to_use = original_params.get('api_used', 'sonic')
            
            if api_to_use == 'nuro':
                # Create song with Nuro API
                new_song = self.yona.create_song(
                    title=modified_params.get('title'),
                    lyrics=modified_params.get('prompt'),  # For Nuro, prompt contains lyrics
                    api='nuro',
                    gender=modified_params.get('gender', 'Female'),
                    genre=modified_params.get('genre', 'Pop'),
                    mood=modified_params.get('mood', 'Happy'),
                    timbre=modified_params.get('timbre', 'Powerful'),
                    duration=modified_params.get('duration', 60),
                    mv=modified_params.get('mv', 'sonic-v4')
                )
            else:
                # Create song with Sonic API
                new_song = self.yona.create_song(
                    title=modified_params.get('title'),
                    lyrics=modified_params.get('prompt'),
                    style=modified_params.get('style'),
                    negative_tags=modified_params.get('negative_tags'),
                    make_instrumental=modified_params.get('make_instrumental', False),
                    mv=modified_params.get('mv', 'sonic-v4'),
                    gpt_description_prompt=modified_params.get('gpt_description_prompt'),
                    voice_gender=modified_params.get('voice_gender', 'female')
                )
            
            # If successful, update the feedback record
            if new_song.get('status') != 'failed':
                # Add references to original song and feedback
                new_song['original_song_id'] = song_id
                new_song['feedback_id'] = feedback_id
                
                # Update the feedback record
                self.yona.supabase_client.update_feedback(feedback_id, {
                    'rating': 5,  # Mark as processed with a default rating
                    'processed_at': 'now()',
                    'new_song_id': new_song.get('id')
                })
                
                # Store as a version in the song_versions table
                version_data = {
                    'song_id': song_id,
                    'title': new_song.get('title'),
                    'lyrics': new_song.get('lyrics'),
                    'audio_url': new_song.get('audio_url'),
                    'params_used': modified_params
                }
                self.yona.supabase_client.store_song_version(song_id, version_data)
            
            return new_song
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "song_id": song_id,
                "feedback_id": feedback_id
            }
    
    def list_songs(self, limit=10, offset=0):
        """
        List songs from the database
        
        Args:
            limit: Maximum number of songs to return
            offset: Offset for pagination
            
        Returns:
            List of dictionaries containing song data
        """
        logger.info(f"Listing songs (limit: {limit}, offset: {offset})")
        
        try:
            return self.yona.list_songs(limit=limit, offset=offset)
        except Exception as e:
            logger.error(f"Error listing songs: {str(e)}")
            return []
    
    def get_song(self, song_id):
        """
        Get a specific song by ID
        
        Args:
            song_id: ID of the song to retrieve
            
        Returns:
            Dictionary containing the song data
        """
        logger.info(f"Getting song {song_id}")
        
        try:
            song = self.yona.supabase_client.get_song_by_id(song_id)
            if not song:
                logger.error(f"Song {song_id} not found")
                return {"status": "failed", "error": f"Song {song_id} not found"}
            return song
        except Exception as e:
            logger.error(f"Error getting song: {str(e)}")
            return {"status": "failed", "error": str(e), "song_id": song_id}
    
    def get_capability_document(self):
        """
        Get the capability document for the agent
        
        Returns:
            Dictionary containing the capability document
        """
        logger.info("Getting capability document")
        
        try:
            return self.yona.get_capability_document()
        except Exception as e:
            logger.error(f"Error getting capability document: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def get_did_document(self):
        """
        Get the DID document for the agent
        
        Returns:
            Dictionary containing the DID document
        """
        logger.info("Getting DID document")
        
        try:
            return self.yona.get_did_document()
        except Exception as e:
            logger.error(f"Error getting DID document: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def process_user_request(self, user_input):
        """
        Process a natural language request from the user
        
        Args:
            user_input: String containing the user's request
            
        Returns:
            Dictionary with results and response
        """
        logger.info(f"Processing user request: {user_input}")
        
        try:
            return self.yona.process_user_request(user_input)
        except Exception as e:
            logger.error(f"Error processing user request: {str(e)}")
            return {
                'action': 'error',
                'result': None,
                'response': f"Error processing request: {str(e)}"
            }
    
    def _modify_parameters_with_openai(self, original_params, feedback_comments):
        """
        Modify song parameters based on feedback using OpenAI
        
        Args:
            original_params: Original parameters used to create the song
            feedback_comments: User feedback comments
            
        Returns:
            Modified parameters
        """
        logger.info("Modifying parameters based on feedback")
        
        try:
            # Use OpenAI to modify parameters based on feedback
            system_message = """
            You are an AI assistant that helps modify song generation parameters based on user feedback.
            Analyze the feedback and suggest modifications to the original parameters.
            Return a JSON object with the modified parameters.
            """
            
            user_message = f"""
            Original parameters:
            {json.dumps(original_params, indent=2)}
            
            User feedback:
            {feedback_comments}
            
            Please modify the parameters based on the feedback. Return only the JSON object with the modified parameters.
            """
            
            response = self.yona.openai_client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Parse the response
            modified_params_text = response.choices[0].message.content
            modified_params = json.loads(modified_params_text)
            
            logger.info("Parameters modified successfully")
            return modified_params
            
        except Exception as e:
            logger.error(f"Error modifying parameters: {str(e)}")
            # Return original parameters if modification fails
            return original_params
```

## Step 4: Define CrewAI Tools

Create a module to define the CrewAI tools that will expose Yona's functionality:

```python
# yona_tools.py
import logging
from typing import Dict, Any, List
from crewai import Tool
from yona_implementation import YonaImplementationManager

logger = logging.getLogger(__name__)

# Initialize the Yona implementation manager
yona_manager = YonaImplementationManager()

def get_yona_tools() -> List[Tool]:
    """
    Get the list of CrewAI tools that expose Yona's functionality
    
    Returns:
        List of CrewAI Tool objects
    """
    logger.info("Creating Yona tools for CrewAI")
    
    tools = [
        Tool(
            name="generate_song",
            description="Generate a song based on a prompt",
            func=lambda prompt, api="sonic", **kwargs: yona_manager.generate_song(prompt, api, **kwargs)
        ),
        Tool(
            name="process_feedback",
            description="Process feedback for a song to create an improved version",
            func=lambda song_id, feedback_id: yona_manager.process_feedback(song_id, feedback_id)
        ),
        Tool(
            name="list_songs",
            description="List songs from the database",
            func=lambda limit=10, offset=0: yona_manager.list_songs(limit, offset)
        ),
        Tool(
            name="get_song",
            description="Get a specific song by ID",
            func=lambda song_id: yona_manager.get_song(song_id)
        ),
        Tool(
            name="get_capability_document",
            description="Get the capability document for the agent",
            func=lambda: yona_manager.get_capability_document()
        ),
        Tool(
            name="get_did_document",
            description="Get the DID document for the agent",
            func=lambda: yona_manager.get_did_document()
        ),
        Tool(
            name="process_user_request",
            description="Process a natural language request from the user",
            func=lambda user_input: yona_manager.process_user_request(user_input)
        )
    ]
    
    logger.info(f"Created {len(tools)} tools for CrewAI")
    return tools
```

## Step 5: Define the Yona Agent in CrewAI

Create a module to define the CrewAI Agent with the Yona tools:

```python
# yona_crew_agent.py
import logging
from crewai import Agent
from yona_tools import get_yona_tools
from crew_config import OPENAI_KEY

logger = logging.getLogger(__name__)

def create_yona_agent() -> Agent:
    """
    Create a CrewAI Agent for Yona
    
    Returns:
        CrewAI Agent object
    """
    logger.info("Creating Yona CrewAI Agent")
    
    # Get the tools that expose Yona's functionality
    tools = get_yona_tools()
    
    # Create the CrewAI Agent
    yona_agent = Agent(
        role='AI Music Creator',
        goal='Generate music based on prompts, lyrics, feedback, or influences.',
        backstory="""
        Yona is an AI-powered music agent specializing in generating K-pop songs and managing 
        feedback-driven iterations. Yona can create songs from prompts, process feedback to 
        improve songs, and manage a database of created songs. Yona also supports decentralized 
        identity (DID) and the Model Context Protocol (MCP) for secure, authenticated communication.
        """,
        tools=tools,
        verbose=True,
        llm_config={
            "api_key": OPENAI_KEY,
            "model": "gpt-4o"
        }
    )
    
    logger.info("Yona CrewAI Agent created successfully")
    return yona_agent
```

## Step 6: Define CrewAI Tasks

Create a module to define the CrewAI Tasks that Yona will perform:

```python
# yona_crew_tasks.py
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
            context="""
            Use the generate_song tool to create a new song based on the user's prompt.
            The tool will handle concept generation, lyrics creation, and song production.
            
            Example usage:
            ```python
            song = generate_song(
                prompt="Create a happy K-pop song about summer adventures",
                api="sonic",  # or "nuro"
                # Optional parameters:
                style="kpop, upbeat, summer",
                negative_tags="sad, melancholic",
                make_instrumental=False,
                mv="sonic-v4",
                description="A cheerful summer pop song with upbeat vibes"
            )
            ```
            
            For Nuro API, you can also specify:
            - gender: "Female" or "Male"
            - genre: "Pop", "Rock", "Hip Hop/Rap", "R&B/Soul", "Electronic"
            - mood: "Happy", "Dynamic/Energetic", "Sentimental/Melancholic/Lonely", "Chill"
            - timbre: "Powerful", "Sexy/Lazy"
            - duration: 30-240 seconds
            
            Return the song metadata including URLs for the audio, video, and image.
            """
        ),
        Task(
            description='Process user feedback to iteratively improve an existing song.',
            agent=yona_agent,
            expected_output='New song version metadata reflecting feedback improvements.',
            context="""
            Use the process_feedback tool to create a new version of a song based on user feedback.
            You'll need the original song ID and the feedback ID.
            
            Example usage:
            ```python
            new_song = process_feedback(
                song_id="123e4567-e89b-12d3-a456-426614174000",
                feedback_id="123e4567-e89b-12d3-a456-426614174001"
            )
            ```
            
            The tool will:
            1. Retrieve the original song and feedback from the database
            2. Use OpenAI to modify the song parameters based on the feedback
            3. Create a new song with the modified parameters
            4. Store the new song in the database with references to the original song and feedback
            5. Update the feedback record to mark it as processed
            
            Return the new song metadata including URLs for the audio, video, and image.
            """
        ),
        Task(
            description='List songs from the database.',
            agent=yona_agent,
            expected_output='List of songs with metadata.',
            context="""
            Use the list_songs tool to retrieve songs from the database.
            
            Example usage:
            ```python
            songs = list_songs(limit=10, offset=0)
            ```
            
            The tool will return a list of dictionaries containing song data.
            You can format this data to present it to the user in a readable way.
            """
        ),
        Task(
            description='Process a natural language request from the user.',
            agent=yona_agent,
            expected_output='Result of the processed request.',
            context="""
            Use the process_user_request tool to handle natural language requests.
            
            Example usage:
            ```python
            result = process_user_request("Create a song about friendship")
            ```
            
            The tool will:
            1. Analyze the request to determine the intent (create_song, list_songs, get_song)
            2. Extract parameters from the request
            3. Execute the appropriate action
            4. Return the result with a human-readable response
            
            This is useful for handling complex or ambiguous requests.
            """
        )
    ]
    
    logger.info(f"Created {len(tasks)} CrewAI Tasks")
    return tasks
```

## Step 7: Set up Crew Workflow

Create a module to set up the CrewAI Crew with the Yona agent and tasks:

```python
# yona_crew.py
import logging
from crewai import Crew
from yona_crew_agent import create_yona_agent
from yona_crew_tasks import create_yona_tasks

logger = logging.getLogger(__name__)

def create_yona_crew() -> Crew:
    """
    Create a CrewAI Crew with the Yona agent and tasks
    
    Returns:
        CrewAI Crew object
    """
    logger.info("Creating Yona CrewAI Crew")
    
    # Get the agent and tasks
    yona_agent = create_yona_agent()
    tasks = create_yona_tasks()
    
    # Create the crew
    crew = Crew(
        agents=[yona_agent],
        tasks=tasks,
        verbose=True
    )
    
    logger.info("Yona CrewAI Crew created successfully")
    return crew
```

## Step 8: CLI Integration

Create a CLI script to execute Yona tasks through CrewAI:

```python
# yona_crew_cli.py
#!/usr/bin/env python
"""
Yona CrewAI CLI

This script provides a command-line interface for executing Yona tasks through CrewAI.
"""
import argparse
import logging
import json
import sys
from yona_implementation import YonaImplementationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Run Yona Agent tasks through CrewAI')
    
    # Task selection
    parser.add_argument('--task', type=str, choices=['create_song', 'process_feedback', 'list_songs', 'process_request'],
                        help='Task to perform')
    
    # Parameters for create_song
    parser.add_argument('--prompt', type=str, help='Prompt for song creation')
    parser.add_argument('--api', type=str, choices=['sonic', 'nuro'], default='sonic',
                        help='API to use for song creation')
    parser.add_argument('--style', type=str, help='Style tags for the song')
    parser.add_argument('--negative-tags', type=str, help='Negative tags to avoid')
    parser.add_argument('--make-instrumental', action='store_true', help='Make the song instrumental')
    parser.add_argument('--mv', type=str, default='sonic-v4', help='Music video generation type')
    parser.add_argument('--description', type=str, help='Description prompt')
    
    # Nuro-specific parameters
    parser.add_argument('--gender', type=str, choices=['Female', 'Male'], help='Singer gender for Nuro API')
    parser.add_argument('--genre', type=str, help='Genre for Nuro API')
    parser.add_argument('--mood', type=str, help='Mood for Nuro API')
    parser.add_argument('--timbre', type=str, help='Timbre for Nuro API')
    parser.add_argument('--duration', type=int, help='Duration in seconds for Nuro API')
    
    # Parameters for process_feedback
    parser.add_argument('--song-id', type=str, help='ID of the song to process feedback for')
    parser.add_argument('--feedback-id', type=str, help='ID of the feedback to process')
    
    # Parameters for list_songs
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of songs to list')
    parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    
    # Parameters for process_request
    parser.add_argument('--request', type=str, help='Natural language request to process')
    
    # General parameters
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--output', type=str, choices=['text', 'json'], default='text',
                        help='Output format')
    
    args = parser.parse_args()
    
    # Initialize Yona implementation manager
    yona_manager = YonaImplementationManager()
    
    # Interactive mode
    if args.interactive:
        run_interactive_mode(yona_manager)
        return
    
    # Execute the specified task
    if args.task == 'create_song':
        if not args.prompt:
            logger.error("Prompt is required for create_song task")
            parser.print_help()
            sys.exit(1)
        
        # Collect parameters
        kwargs = {}
        if args.style:
            kwargs['style'] = args.style
        if args.negative_tags:
            kwargs['negative_tags'] = args.negative_tags
        if args.make_instrumental:
            kwargs['make_instrumental'] = True
        if args.mv:
            kwargs['mv'] = args.mv
        if args.description:
            kwargs['description'] = args.description
        
        # Add Nuro-specific parameters
        if args.api == 'nuro':
            if args.gender:
                kwargs['gender'] = args.gender
            if args.genre:
                kwargs['genre'] = args.genre
            if args.mood:
                kwargs['mood'] = args.mood
            if args.timbre:
                kwargs['timbre'] = args.timbre
            if args.duration:
                kwargs['duration'] = args.duration
        
        # Execute the task
        result = yona_manager.generate_song(args.prompt, args.api, **kwargs)
        output_result(result, args.output)
    
    elif args.task == 'process_feedback':
        if not args.song_id or not args.feedback_id:
            logger.error("Song ID and feedback ID are required for process_feedback task")
            parser.print_help()
            sys.exit(1)
        
        # Execute the task
        result = yona_manager.process_feedback(args.song_id, args.feedback_id)
        output_result(result, args.output)
    
    elif args.task == 'list_songs':
        # Execute the task
        result = yona_manager.list_songs(args.limit, args.offset)
        output_result(result, args.output)
    
    elif args.task == 'process_request':
        if not args.request:
            logger.error("Request is required for process_request task")
            parser.print_help()
            sys.exit(1)
        
        # Execute the task
        result = yona_manager.process_user_request(args.request)
        output_result(result, args.output)
    
    else:
        logger.error("No task specified")
        parser.print_help()
        sys.exit(1)

def run_interactive_mode(yona_manager):
    """
