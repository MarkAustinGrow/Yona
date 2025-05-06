# Yona Codebase Documentation

## 1. Project Structure

The project is structured as follows:

- `src/`: Main source code directory
  - `api/`: API endpoints for MCP implementation
  - `config/`: Configuration files
  - `coral_protocol/`: Coral Protocol LangChain integration
    - `langchain/`: LangChain implementation for Coral Protocol
      - `__init__.py`: Package initialization
      - `config.py`: Configuration for Coral Protocol LangChain
      - `runnable.py`: Main implementation of CoralRunnable
  - `examples/`: Example scripts
  - `identity/`: DID management for MCP implementation
  - `migrations/`: Database migration scripts
  - `protocol/`: Protocol handling for MCP implementation
  - Multiple Python modules for different functionalities
- `lyrics/`: Directory containing lyrics files for song creation
- `tests/`: Test files for the project
- CrewAI integration files:
  - `crew_config.py`: Configuration for CrewAI integration
  - `yona_implementation.py`: Bridge between CrewAI and Yona
  - `yona_tools.py`: CrewAI tools for Yona functionality
  - `yona_crew_agent.py`: CrewAI Agent definition
  - `yona_crew_tasks.py`: CrewAI Tasks definition
  - `yona_crew.py`: CrewAI Crew setup
  - `yona_crew_cli.py`: CLI for CrewAI integration
  - `test_yona_crew.py`: Tests for CrewAI integration

## 2. Dependencies and Imports

### Core Dependencies
- Python standard libraries: `os`, `sys`, `time`, `json`, `logging`, `argparse`, `tempfile`, `base64`, `uuid`
- External libraries:
  - `dotenv`: Environment variable management
  - `httpx`: HTTP client for API calls
  - `supabase`: Supabase client for database operations
  - `openai`: OpenAI API client
  - `flask`: Web framework for API endpoints
  - `cryptography`: Cryptographic operations for DID management
  - `crewai`: Framework for orchestrating autonomous AI agents
  - `crewai-tools`: Set of tools for the crewAI framework

### Import Structure by File

#### src/config/config.py
```python
import os
from dotenv import load_dotenv
```

#### src/music_api.py
```python
import os
import json
import time
import logging
import httpx
from typing import Dict, Any, Optional, List, Union
from src.config.config import MUSICAPI_KEY, MUSICAPI_BASE_URL, NURO_BASE_URL
```

#### src/supabase_client.py
```python
import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from supabase import create_client
from src.config.config import SUPABASE_URL, SUPABASE_KEY
```

#### src/create_song.py
```python
import os
import sys
import time
import json
import logging
import argparse
from dotenv import load_dotenv
from src.config.config import MUSICAPI_KEY, YONA_PERSONA
from src.music_api import MusicAPI
from src.supabase_client import SupabaseClient
```

#### src/generate_song.py
```python
import os
import sys
import time
import json
import logging
import argparse
import tempfile
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.agent import YonaAgent
from src.music_api import MusicAPI
from src.supabase_client import SupabaseClient
from src.config.config import MUSICAPI_KEY, OPENAI_KEY
```

#### yona_tools.py (CrewAI Integration)
```python
import logging
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from yona_implementation import YonaImplementationManager
```

## 3. Configuration (src/config/config.py)

The application uses the following environment variables:

| Variable Name | Purpose | Current Value |
|--------------|---------|---------------|
| `OPENAI_KEY` | API key for OpenAI | sk-proj-s94oRCKZLb8mc4bgGMzko460MEE4dJky9tIJfax... |
| `MUSICAPI_KEY` | API key for MusicAPI.ai | 64cbe729d7ee5f752f8ae086c9e5fe7b |
| `SUPABASE_URL` | URL for Supabase database | https://oeexwetwqsooikroobgm.supabase.co |
| `SUPABASE_KEY` | API key for Supabase | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| `YOUTUBE_API_KEY` | API key for YouTube | AIzaSyDWkbZ30x3vmve8Kuh8O9-DsVXy-MqWigQ |
| `YOUTUBE_CLIENT_ID` | Client ID for YouTube API | 570900247172-eh86h9e6s0sarc41m0elik6ub4iv858q.apps.googleusercontent.com |
| `YOUTUBE_CLIENT_SECRET` | Client secret for YouTube API | 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 |

Additional configuration:
- `OPENAI_MODEL`: Set to "gpt-4o" for supporting structured outputs
- `MUSICAPI_BASE_URL`: "https://api.musicapi.ai"
- `NURO_BASE_URL`: "https://api.musicapi.ai/api/v1/nuro"
- `YONA_PERSONA`: Dictionary defining Yona's personality and style
- `DEFAULT_SONG_PARAMETERS`: Default parameters for song creation

## 4. Database Schema

Based on the code analysis, the Supabase database includes the following tables:

### Songs Table

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | uuid (primary key) | Unique ID for the song |
| `title` | text | Title of the song |
| `persona_id` | text | Reference to persona ID (typically 'direct_generation') |
| `lyrics` | text | Full lyrics of the song |
| `audio_url` | text | URL to the generated audio |
| `video_url` | text | URL to the generated video |
| `image_url` | text | URL to the generated image |
| `style` | text | Style tags for the song |
| `make_instrumental` | boolean | Whether the song is instrumental |
| `mv` | text | Music video generation type |
| `gpt_description` | text | Description prompt used |
| `negative_tags` | text | Tags to avoid in generation |
| `duration` | float | Duration of the song in seconds |
| `params_used` | jsonb | JSON object with all parameters used |
| `processor_did` | text | DID of the agent that processed the song (for MCP) |
| `original_song_id` | uuid | Reference to the original song (for songs created from feedback) |
| `feedback_id` | uuid | Reference to the feedback that prompted this song |

### Feedback Table

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | uuid (primary key) | Unique ID for the feedback |
| `song_id` | uuid | Reference to the song being commented on |
| `comments` | text | User feedback comments |
| `rating` | integer | Rating value (NULL indicates unprocessed feedback) |
| `created_at` | timestamp | When the feedback was created |

### Song Versions Table

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | uuid (primary key) | Unique ID for the version |
| `song_id` | uuid | Reference to the original song |
| `version_number` | integer | Sequential version number |
| `title` | text | Title of this version |
| `lyrics` | text | Lyrics for this version |
| `audio_url` | text | URL to the generated audio |
| `params_used` | jsonb | Parameters used for this version |
| `created_at` | timestamp | When the version was created |

### Influence Music Table

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | uuid (primary key) | Unique ID for the influence music record |
| `url` | text | URL to the reference music |
| `analysis` | jsonb | Analysis data including BPM, key, and moods |
| `song_id` | uuid | Reference to the song created from this influence (NULL indicates unprocessed) |
| `created_at` | timestamp | When the record was created |

## 5. Feedback and Versioning System

The codebase includes a comprehensive feedback and versioning system that allows for iterative improvement of songs:

### Feedback Processing

1. **Feedback Collection**: Users can provide feedback on songs, which is stored in the `feedback` table.
2. **Feedback Processing**: Two methods are available for processing feedback:
   - **Manual Processing**: Using `create_song_from_feedback.py` to process a specific feedback record
   - **Automatic Processing**: Using `continuous_feedback_processor.py` to continuously monitor and process feedback

### Influence Music Processing

The system can also create songs inspired by existing music:

1. **Influence Music Collection**: Reference music URLs and their analysis are stored in the `influence_music` table.
2. **Analysis Data**: Each record contains analysis data including:
   - BPM (Beats Per Minute)
   - Musical key
   - Moods with confidence scores
3. **Processing Flow**:
   - The `process_influence_music()` function processes unprocessed records
   - OpenAI is used to generate optimized parameters based on the musical characteristics
   - A new song is created using these parameters
   - The song is stored in the database and linked to the influence music record
   - The influence music record is marked as processed

### Continuous Feedback Processor

The `continuous_feedback_processor.py` script:
- Runs as a daemon process, checking for unprocessed feedback and influence music every hour
- Processes one record per cycle to manage API usage
- For feedback: Uses OpenAI to intelligently modify song parameters based on feedback
- For influence music: Uses OpenAI to generate parameters based on musical characteristics
- Creates new songs with the generated parameters
- Stores the new songs in the database with appropriate references
- Marks records as processed
- Includes robust error handling and logging

### Song Versioning

The system maintains a history of song versions:
- Each new version of a song is stored in the `song_versions` table
- Version numbers are automatically incremented
- Parameters used for each version are stored to track the evolution of a song
- Original songs and their derivatives are linked through the `original_song_id` field

### AI-Powered Parameter Modification

The `modify_parameters_with_openai()` function:
- Takes original parameters and feedback comments
- Uses structured prompts to guide OpenAI in making appropriate modifications
- Returns modified parameters as a JSON object
- Maintains the core identity of the song while addressing specific feedback

## 6. Key Classes and Methods

### YonaAgent (src/agent.py)

```python
class YonaAgent:
    def __init__(self, openai_api_key=None, simulation_mode=False, did_domain="yona.ai", private_key_path=None)
    def generate_song_concept(self, prompt)
    def generate_lyrics(self, concept)
    def create_song(self, title, lyrics, style=None, negative_tags=None, make_instrumental=False,
                   mv='sonic-v4', gpt_description_prompt=None, voice_gender='female', max_attempts=60,
                   check_interval=30)
    def list_songs(self, limit=10, offset=0)
    def process_user_request(self, user_input)
    def get_capability_document()
    def get_did_document()
    def get_auth_headers(request_data=None)
    def save_private_key(path)
    def _analyze_request(self, user_input)
```

### DIDManager (src/identity/did_manager.py)

```python
class DIDManager:
    def __init__(self, did_domain="yona.ai", private_key_path=None, simulation_mode=False)
    def _generate_keys()
    def _load_private_key(private_key_path)
    def _create_did_document()
    def get_did_document()
    def sign_request(data)
    def verify_signature(data, signature, did_document)
    def save_private_key(path)
    def get_auth_headers(request_data=None)
```

### CapabilityDocument (src/protocol/capability_document.py)

```python
class CapabilityDocument:
    def __init__(self, did, agent_name="Yona AI", agent_description="An AI K-pop star that creates songs based on prompts and feedback")
    def _add_default_services()
    def add_service(service_id, service_type, description, input_schema, output_schema)
    def update_protocols(supported=None, preferred=None, versions=None)
    def generate()
    def generate_json(pretty=True)
    def save_to_file(path)
```

### YonaAPI (src/api/endpoints.py)

```python
class YonaAPI:
    def __init__(self, did_domain="yona.ai", private_key_path=None, simulation_mode=False)
    def _register_routes()
    def get_capabilities()
    def get_did_document()
    def health_check()
    def run(host='0.0.0.0', port=5000, debug=False)
```

### MusicAPI (src/music_api.py)

```python
class MusicAPI:
    def __init__(self, api_key=None, base_url=None, simulation_mode=False)
    def create_song(self, prompt, title=None, style=None, negative_tags=None, make_instrumental=False, 
                   mv='sonic-v4', gpt_description_prompt=None, voice_gender='female')
    def check_song_status(self, task_id)
    def create_song_nuro(self, lyrics, gender=None, genre=None, mood=None, timbre=None, duration=None)
    def check_song_status_nuro(self, task_id)
    def create_persona(self, name, description, continue_clip_id=None)
    def create_cover(self, continue_clip_id, prompt, title=None, style=None, negative_tags=None,
                    make_instrumental=False, mv='sonic-v4', gpt_description_prompt=None, voice_gender='female')
```

### SupabaseClient (src/supabase_client.py)

```python
class SupabaseClient:
    def __init__(self, url=None, key=None, simulation_mode=False)
    def store_song_data(self, song_data)
    def get_song_by_id(self, song_id)
    def list_songs(self, limit=10, offset=0)
    def get_feedback_by_id(self, feedback_id)
    def update_feedback(self, feedback_id, data)
    def get_unprocessed_feedback()
    def store_song_version(self, original_song_id, version_data)
    def get_unprocessed_influence_music(self, limit=1)
    def mark_influence_music_processed(self, record_id, song_id)
```

### YonaCoralAdapter (src/coral_langchain.py)

```python
class YonaCoralAdapter:
    def __init__(self, yona_agent, coral_server_url, openai_api_key=None, did_domain="yona.ai", private_key_path=None)
    def _get_private_key_bytes()
    def _create_coral_runnable()
    def register_with_coral_server()
    def call_agent(self, agent_did, function_name, **kwargs)
    def discover_agents()
    def get_agent_capabilities(self, agent_did)
    def start_server(self, host='0.0.0.0', port=5001)
```

### CoralRunnable (src/coral_protocol/langchain/runnable.py)

```python
class CoralRunnable:
    def __init__(self, functions, config)
    def _register_with_server()
    def _sign_payload(self, payload)
    def call_agent(self, agent_did, function_name, **kwargs)
    def discover_agents()
    def get_agent_capabilities(self, agent_did)
    def start_server(self, host='0.0.0.0', port=5001)
    def _run_server(self, host, port)
    def stop_server()
```

### CoralRunnableConfig (src/coral_protocol/langchain/config.py)

```python
class CoralRunnableConfig:
    def __init__(self, server_url, did, private_key, capability_document, agent_name=None, agent_description=None)
```

### YonaImplementationManager (yona_implementation.py)

```python
class YonaImplementationManager:
    def __init__(self, did_domain="yona.ai", private_key_path=None)
    def generate_song(self, prompt, api="sonic", **kwargs)
    def process_feedback(self, song_id, feedback_id)
    def list_songs(self, limit=10, offset=0)
    def get_song(self, song_id)
    def get_capability_document()
    def get_did_document()
    def process_user_request(self, user_input)
    def _modify_parameters_with_openai(self, original_params, feedback_comments)
```

### CrewAI Tools (yona_tools.py)

```python
class GenerateSongTool(BaseTool):
    def _run(self, prompt: str, api: str = "sonic", **kwargs)

class ProcessFeedbackTool(BaseTool):
    def _run(self, song_id: str, feedback_id: str)

class ListSongsTool(BaseTool):
    def _run(self, limit: int = 10, offset: int = 0)

class GetSongTool(BaseTool):
    def _run(self, song_id: str)

class GetCapabilityDocumentTool(BaseTool):
    def _run(self)

class GetDIDDocumentTool(BaseTool):
    def _run(self)

class ProcessUserRequestTool(BaseTool):
    def _run(self, user_input: str)

def get_yona_tools() -> List[BaseTool]
```

## 7. Command-line Scripts

### create_song.py

Creates a song using the MusicAPI with provided lyrics or prompt.

Parameters:
- `--title`: Title of the song (required)
- `--lyrics-file`: Path to lyrics file (mutually exclusive with --prompt)
- `--prompt`: Direct text prompt (mutually exclusive with --lyrics-file)
- `--style`: Style tags for the song
- `--mv`: Music video generation type (default: 'sonic-v4')
- `--negative-tags`: Negative tags to avoid
- `--instrumental`: Make the song instrumental (flag)
- `--description`: Description prompt
- `--voice-gender`: Voice gender (default: 'female')
- `--max-attempts`: Maximum status check attempts (default: 60)
- `--check-interval`: Seconds between status checks (default: 30)

### run_api_server.py

Runs the API server for the MCP implementation.

Parameters:
- `--host`: Host to bind to (default: '127.0.0.1')
- `--port`: Port to bind to (default: 5000)
- `--debug`: Run in debug mode (flag)
- `--did-domain`: Domain for the did:web identifier (default: 'yona.ai')
- `--private-key`: Path to a file containing a private key
- `--simulation`: Run in simulation mode (flag)

Example usage:
```bash
# Run the API server
python run_api_server.py

# Run with custom host and port
python run_api_server.py --host 0.0.0.0 --port 8000

```

### test_mcp.py

Tests the MCP implementation without running the full API server.

Parameters:
- `--simulation`: Run in simulation mode (flag)

Example usage:
```bash
# Test the MCP implementation
python test_mcp.py

```

### generate_song.py

Generates a song concept and lyrics using AI, then creates the song.

Parameters:
- `prompt`: Concept prompt for generating the song idea (required)
- `--api`: API to use for song generation (choices: 'sonic', 'nuro', default: 'sonic')

Sonic API parameters (used when --api=sonic):
- `--override-style`: Override LLM-generated style tags
- `--override-negative-tags`: Override LLM-generated negative tags
- `--override-instrumental`: Override LLM decision on instrumental (flag)
- `--override-mv`: Override LLM-generated music video type
- `--override-description`: Override LLM-generated description

Nuro API parameters (used when --api=nuro):
- `--gender`: Singer's gender (choices: 'Female', 'Male')
- `--genre`: Genre of the song (see examples/nuro_api_example.md for options)
- `--mood`: Mood of the song (see examples/nuro_api_example.md for options)
- `--timbre`: Timbre of the song (see examples/nuro_api_example.md for options)
- `--duration`: Duration in seconds, 30-240

Common parameters:
- `--max-attempts`: Maximum status check attempts (default: 60)
- `--check-interval`: Seconds between status checks (default: 30)

Example usage:
```bash
# Using Sonic API (default)
python src/generate_song.py "Create a happy pop song about summer adventures"

# Using Nuro API
python src/generate_song.py "Create a happy pop song about summer adventures" --api nuro --gender Female --genre Pop --mood Happy
```

### list_songs.py

Lists the songs stored in the Supabase database.

### yona_cli.py

Provides a command-line interface for interacting with Yona in an agentic way.

Parameters:
- `--simulation`: Run in simulation mode without making API calls (flag)
- `--interactive`: Run in interactive mode, allowing multiple requests (flag)
- `--request`: Process a single request and exit (e.g., "Create a song about friendship")

Example usage:
```bash
# Interactive mode
python src/yona_cli.py --interactive

# Single request mode
python src/yona_cli.py --request "Create a song about summer"

```

### create_song_from_feedback.py

Creates a new song based on feedback for an existing song.

Parameters:
- `--song-id`: ID of the original song (required)
- `--feedback-id`: ID of the feedback to process (required)
- `--simulation`: Run in simulation mode (flag)

Example usage:
```bash
# Process specific feedback
python src/create_song_from_feedback.py --song-id 123e4567-e89b-12d3-a456-426614174000 --feedback-id 123e4567-e89b-12d3-a456-426614174001

```

### continuous_feedback_processor.py

Runs continuously, checking for unprocessed feedback every hour and creating new songs based on the feedback.

No command-line parameters are required, but the script can be run with the batch file `run_feedback_processor.bat`.

Example usage:
```bash
# Run directly
python src/continuous_feedback_processor.py

# Run using batch file
run_feedback_processor.bat
```

### yona_crew_cli.py

Provides a command-line interface for executing Yona tasks through CrewAI.

Parameters:
- `--task`: Task to perform (choices: 'create_song', 'process_feedback', 'list_songs', 'process_request')
- `--prompt`: Prompt for song creation
- `--api`: API to use for song creation (choices: 'sonic', 'nuro', default: 'sonic')
- `--style`: Style tags for the song
- `--negative-tags`: Negative tags to avoid
- `--make-instrumental`: Make the song instrumental (flag)
- `--mv`: Music video generation type (default: 'sonic-v4')
- `--description`: Description prompt
- `--gender`: Singer gender for Nuro API (choices: 'Female', 'Male')
- `--genre`: Genre for Nuro API
- `--mood`: Mood for Nuro API
- `--timbre`: Timbre for Nuro API
- `--duration`: Duration in seconds for Nuro API
- `--song-id`: ID of the song to process feedback for
- `--feedback-id`: ID of the feedback to process
- `--limit`: Maximum number of songs to list (default: 10)
- `--offset`: Offset for pagination (default: 0)
- `--request`: Natural language request to process
- `--interactive`: Run in interactive mode (flag)
- `--output`: Output format (choices: 'text', 'json', default: 'text')
- `--use-crew`: Use CrewAI to execute tasks (flag)

Example usage:
```bash
# Interactive mode
python yona_crew_cli.py --interactive

# Create a song
python yona_crew_cli.py --task create_song --prompt "Create a happy K-pop song about summer adventures"

# Process feedback
python yona_crew_cli.py --task process_feedback --song-id "song_id" --feedback-id "feedback_id"

# List songs
python yona_crew_cli.py --task list_songs --limit 10 --offset 0

# Process a natural language request
python yona_crew_cli.py --task process_request --request "Create a song about friendship"

# Use CrewAI to execute tasks
python yona_crew_cli.py --task create_song --prompt "Create a happy K-pop song about summer adventures" --use-crew
```

### test_coral_langchain.py

Tests the Coral Protocol LangChain integration with Yona.

Parameters:
- `--server-url`: URL of the Coral server (required)
- `--test`: Test to run (choices: 'connection', 'capabilities', 'call', 'server', default: 'connection')
- `--agent-did`: DID of the agent to interact with (required for 'capabilities' and 'call' tests)
- `--function`: Function to call on the agent (required for 'call' test)
- `--args`: JSON string of arguments to pass to the function (optional for 'call' test)
- `--host`: Host to bind server to (default: '0.0.0.0', used for 'server' test)
- `--port`: Port to bind server to (default: 5001, used for 'server' test)

Example usage:
```bash
# Test connection to a Coral server
python test_coral_langchain.py --server-url http://coral.pushcollective.club/sse --test connection

# Test getting agent capabilities
python test_coral_langchain.py --server-url http://coral.pushcollective.club/sse --test capabilities --agent-did did:web:example.com

# Test calling an agent function
python test_coral_langchain.py --server-url http://coral.pushcollective.club/sse --test call --agent-did did:web:example.com --function create_song --args '{"prompt": "Create a happy K-pop song about summer adventures"}'

# Start a Coral server
python test_coral_langchain.py --server-url http://coral.pushcollective.club/sse --test server --host 0.0.0.0 --port 5001
```

### test_yona_crew.py

Tests the CrewAI integration with Yona.

Example usage:
```bash
# Test the CrewAI integration
python test_yona_crew.py
```

## 8. Integration Points

1. **OpenAI API Integration**:
   - Used in YonaAgent for generating song concepts and lyrics
   - Configured with the OPENAI_KEY from environment variables

2. **MusicAPI.ai Integration**:
   - Core integration for song creation, cover creation, and persona creation
   - Handles API requests, payload formatting, and response processing

3. **Supabase Integration**:
   - Used for storing song data, including metadata and generated URLs
   - Configured with SUPABASE_URL and SUPABASE_KEY from environment variables

4. **MCP Integration**:
   - Provides decentralized identity and capability document generation
   - Enables secure, authenticated communication between agents
   - Implemented using the Model Context Protocol framework

5. **Coral Protocol LangChain Integration**:
   - Enables Yona to connect to a Coral Protocol server using LangChain
   - Allows Yona to register its capabilities with the Coral server
   - Enables discovering other agents on the Coral server
   - Provides functionality for calling functions on other agents
   - Implemented locally in the `src/coral_protocol/langchain` directory
   - Exposes Yona's song creation, feedback processing, and song listing capabilities to other agents

6. **CrewAI Integration**:
   - Enables Yona to be used as an agent within the CrewAI framework
   - Provides a bridge between Yona's functionality and CrewAI's agent system
   - Exposes Yona's capabilities as CrewAI tools
   - Allows for orchestrating Yona with other agents in a crew

## 9. API Options

The system supports two different APIs for song generation, each with its own strengths and parameters:

### Sonic API

The original API used by the Yona project, with the following parameters:
- `prompt`: Lyrics or text prompt for the song
- `title`: Title of the song
- `style`: Style tags for the song (e.g., "pop, upbeat, summer")
- `negative_tags`: Tags to avoid in generation
- `make_instrumental`: Whether the song should be instrumental
- `mv`: Music video generation type (sonic-v3-5 or sonic-v4)
- `gpt_description_prompt`: Additional description for guiding generation
- `voice_gender`: Gender of the singer's voice (female or male)

Example usage:
```bash
# Using Sonic API (default)
python src/generate_song.py "Create a happy pop song about summer adventures"

# With additional Sonic API parameters
python src/generate_song.py "Create a happy pop song about summer adventures" \
  --override-style "pop, upbeat, summer" \
  --override-negative-tags "sad, melancholic" \
  --override-instrumental \
  --override-mv "sonic-v4" \
  --override-description "A cheerful summer pop song with upbeat vibes"
```

### Nuro API

A newer API that provides more specific control over song parameters:
- `lyrics`: Lyrics for the song
- `gender`: Singer's gender (Female or Male)
- `genre`: Genre of the song (Pop, Rock, Folk, etc.)
- `mood`: Mood of the song (Happy, Sad, Energetic, etc.)
- `timbre`: Timbre of the singer's voice (Warm, Bright, Husky, etc.)
- `duration`: Duration in seconds (30-240)

Example usage:
```bash
# Using Nuro API
python src/generate_song.py "Create a happy pop song about summer adventures" --api nuro

# With additional Nuro API parameters
python src/generate_song.py "Create a happy pop song about summer adventures" \
  --api nuro \
  --gender "Female" \
  --genre "Pop" \
  --mood "Happy" \
  --timbre "Bright" \
  --duration 180
```

### Automatic Fallback Mechanism

The system includes an automatic fallback mechanism that switches to the Nuro API if the Sonic API is under maintenance:

1. When the Sonic API returns a maintenance error, the system automatically falls back to the Nuro API
2. The system maps Sonic API parameters to Nuro API parameters:
   - `voice_gender` → `gender` (Female/Male)
   - `style_tags` → `genre` and `mood` (using intelligent mapping)
3. The fallback is logged for transparency
4. The song is created using the Nuro API with the mapped parameters
5. All subsequent status checks use the Nuro API methods

This ensures continuous operation even when one API is unavailable, making the system more resilient.

## 10. Data Flow

### Traditional Workflow (create_song.py)
1. User provides a song title and lyrics/prompt via command line
2. Application loads environment variables and initializes clients
3. MusicAPI client sends request to create the song
4. Application checks song status repeatedly until complete
5. Once complete, song data is stored in Supabase
6. URLs for the generated audio/video/image are returned to user

### AI-Assisted Workflow (generate_song.py)
1. User provides a concept prompt via command line
2. Application initializes YonaAgent
3. YonaAgent generates a song concept using OpenAI
4. YonaAgent generates lyrics based on the concept
5. MusicAPI client sends request to create the song
6. Application checks song status repeatedly until complete
7. Once complete, song data is stored in Supabase
8. URLs for the generated audio/video/image are returned to user

### Agentic Workflow (yona_cli.py)
1. User provides a natural language request (e.g., "Create a song about friendship")
2. YonaAgent analyzes the request using OpenAI to determine intent and extract parameters
3. Based on the intent, YonaAgent takes appropriate actions:
   - For "create_song": Generates concept, lyrics, and creates the song
   - For "list_songs": Retrieves songs from Supabase
   - For "get_song": Retrieves a specific song from Supabase
4. YonaAgent returns a response to the user with relevant information
5. In interactive mode, the process repeats for each user request

### MCP-Enabled Feedback Processing Workflow
1. User runs the continuous_feedback_processor.py script or create_song_from_feedback.py
2. YonaAgent is initialized with DID capabilities (did_domain="yona.ai")
3. The agent's DID is shared with MusicAPI for authenticated requests
4. When processing feedback:
   - Original song and feedback are retrieved from Supabase
   - Parameters are modified based on feedback using OpenAI
   - A new song is created with MusicAPI (with DID-authenticated requests)
   - The new song is stored in Supabase with the processor's DID
   - The feedback is marked as processed
5. The processor_did field allows tracking which agent processed each feedback

### Influence Music Processing Workflow
1. User runs the continuous_feedback_processor.py script
2. YonaAgent is initialized with DID capabilities
3. The system checks for unprocessed influence music records (where song_id is NULL)
4. For each unprocessed record:
   - The URL and analysis data (BPM, key, moods) are extracted
   - OpenAI is used to generate optimized parameters based on the musical characteristics
   - These parameters include style, negative tags, description, and even sample lyrics
   - A new song is created using the Sonic API with these parameters
   - The song status is monitored until completion
   - The song data is stored in Supabase with a reference to the original analysis
   - The influence music record is marked as processed by setting its song_id
5. This workflow enables creating songs inspired by existing music while maintaining creative uniqueness

### Coral Protocol LangChain Integration Workflow
1. User runs the test_coral_langchain.py script
2. YonaAgent is initialized with DID capabilities
3. YonaCoralAdapter is initialized with the YonaAgent and Coral server URL
4. The adapter creates a CoralRunnable with Yona's functions (create_song, process_feedback, list_songs)
5. The adapter registers with the Coral server, sharing Yona's capabilities
6. The adapter can:
   - Discover other agents on the Coral server
   - Get the capabilities of other agents
   - Call functions on other agents
   - Start a server to listen for requests from other agents
7. When another agent calls a function on Yona:
   - The request is received by Yona's server
   - The function is executed with the provided arguments
   - The result is returned to the calling agent
8. When Yona calls a function on another agent:
   - The request is sent to the Coral server
   - The Coral server routes the request to the target agent
   - The target agent executes the function and returns the result
   - The result is returned to Yona

### CrewAI Integration Workflow
1. User runs the yona_crew_cli.py script
2. YonaImplementationManager is initialized to bridge CrewAI and Yona
3. CrewAI tools are created to expose Yona's functionality
4. Based on the user's command:
   - For direct execution: The appropriate YonaImplementationManager method is called
   - For CrewAI execution: A CrewAI Crew is created with the Yona agent and tasks
5. The task is executed, and the result is returned to the user
6. In interactive mode, the process repeats for each user request

## 11. Recently Fixed Issues

1. Database schema compatibility issue:
   - The code was attempting to store a `clip_id` field that didn't exist in the Supabase schema
   - Fixed by removing the `clip_id` field and adding `persona_id` with value 'direct_generation'
   - Changes made to both create_song.py and generate_song.py

2. CrewAI integration compatibility issue:
   - The CrewAI API had changed, requiring updates to the tool implementation
   - Fixed by updating the import from `from crewai import Tool` to `from crewai.tools import BaseTool`
   - Modified all tool classes to inherit from `BaseTool` instead of `Tool`
   - Updated the return type annotation in the `get_yona_tools()` function to use `BaseTool` instead of `Tool`
   - These changes align with the current CrewAI API, which requires custom tools to inherit from `BaseTool` in the `crewai.tools` module

3. Coral Protocol LangChain integration issue:
   - The `langchain-coral` package was not available on PyPI and was causing Docker build failures
   - Fixed by implementing a local version of the Coral Protocol LangChain integration in the `src/coral_protocol/langchain` directory
   - Updated the Dockerfile to use Python 3.11 instead of Python 3.10 for better compatibility
   - Updated the import in `src/coral_langchain.py` to use the local implementation instead of the external package
   - Created a script to fix the requirements.txt file on the server to remove the problematic dependency
   - These changes allow Yona to connect to a Coral Protocol server without relying on an external package
