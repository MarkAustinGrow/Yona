# Yona Codebase Documentation

## 1. Project Structure

The project is structured as follows:

- `src/`: Main source code directory
  - `config/`: Configuration files
  - `examples/`: Example scripts
  - `identity/`: DID management for authentication
  - `migrations/`: Database migration scripts
  - `protocol/`: Protocol handling for API capabilities
  - Multiple Python modules for different functionalities
- `lyrics/`: Directory containing lyrics files for song creation
- `tests/`: Test files for the project

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
| `processor_did` | text | DID of the agent that processed the song |
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
    def __init__(self, openai_api_key=None, did_domain="yona.ai", private_key_path=None)
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
    def __init__(self, did_domain="yona.ai", private_key_path=None)
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
    def __init__(self, did_domain="yona.ai", private_key_path=None)
    def _register_routes()
    def get_capabilities()
    def get_did_document()
    def health_check()
    def run(host='0.0.0.0', port=5000, debug=False)
```

### MusicAPI (src/music_api.py)

```python
class MusicAPI:
    def __init__(self, api_key=None, base_url=None)
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
    def __init__(self, url=None, key=None)
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

Runs the API server.

Parameters:
- `--host`: Host to bind to (default: '127.0.0.1')
- `--port`: Port to bind to (default: 5000)
- `--debug`: Run in debug mode (flag)
- `--did-domain`: Domain for the did:web identifier (default: 'yona.ai')
- `--private-key`: Path to a file containing a private key

Example usage:
```bash
# Run the API server
python run_api_server.py

# Run with custom host and port
python run_api_server.py --host 0.0.0.0 --port 8000
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

### Feedback Processing Workflow
1. User runs the continuous_feedback_processor.py script or create_song_from_feedback.py
2. YonaAgent is initialized with DID capabilities (did_domain="yona.ai")
3. When processing feedback:
   - Original song and feedback are retrieved from Supabase
   - Parameters are modified based on feedback using OpenAI
   - A new song is created with MusicAPI
   - The new song is stored in Supabase with the processor's DID
   - The feedback is marked as processed

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

## 11. Recently Fixed Issues

1. Database schema compatibility issue:
   - The code was attempting to store a `clip_id` field that didn't exist in the Supabase schema
   - Fixed by removing the `clip_id` field and adding `persona_id` with value 'direct_generation'
   - Changes made to both create_song.py and generate_song.py

2. Song creation timeout issue:
   - Increased max_attempts from 30 to 60
   - Added check_interval parameter (default: 30 seconds)
   - Improved error handling and logging
   - Added logic to consider a song successful if it has an audio URL even if status is still "pending"

3. Continuous feedback processor syntax error:
   - Fixed an unterminated string literal in the `process_influence_music` function
   - Completed the `song_data_for_db` dictionary definition
   - Added missing code for storing song data and marking influence music as processed
   - Added the `check_for_unprocessed_influence_music` function to the main loop
   - This fix enables the system to process influence music records automatically

4. Reversion to NuroAPI branch:
   - Removed Coral Protocol integration
   - Simplified the codebase to focus on core song generation functionality
   - Ensured compatibility with both Sonic API and Nuro API
   - Updated Docker configuration for cleaner builds

## 12. Backup Recommendation

To prevent code damage during major changes:
1. Commit changes frequently with descriptive messages
2. Create Git branches for major features
3. Consider using Git tags to mark stable versions
4. Implement automated tests for core functionality
5. Document all environment variables and configurations

## 13. Deployment

The application is deployed using Docker containers on a Linode server:

### Server Information
- **IP Address**: 172-236-28-244
- **Domain**: yona.club
- **Operating System**: Ubuntu 22.04 LTS

### Docker Setup
The application is containerized using Docker and orchestrated with Docker Compose:
- `Dockerfile`: Defines the application image based on Python
- `docker-compose.yml`: Defines two services:
  - **yona-api**: Runs the API server on port 5000
  - **yona-feedback-processor**: Runs the continuous feedback processor

### Deployment Architecture
1. The Docker containers run on the Linode server
2. Nginx serves as a reverse proxy, routing requests from yona.club to the API container
3. SSL/TLS is provided by Let's Encrypt for secure HTTPS connections
4. Environment variables are stored in a .env file on the server (not included in the repository)
5. Logs are stored in the logs/ directory, which is mounted as a volume in the containers

### Deployment Process
Detailed deployment instructions are available in the DEPLOYMENT_GUIDE.md file, which covers:
- Setting up the Linode server
- Installing Docker and Docker Compose
- Configuring Nginx as a reverse proxy
- Setting up SSL with Let's Encrypt
- Monitoring and maintenance procedures

### Accessing the Deployed Application
- **API Endpoints**: https://yona.club/
- **Health Check**: https://yona.club/health
- **Capabilities Document**: https://yona.club/capabilities
- **DID Document**: https://yona.club/.well-known/did.json

## 14. Error Handling Best Practices

### Avoid Silent Fallbacks

The codebase should avoid silent fallbacks that mask real issues. Instead:

1. **Detailed Error Reporting**: All errors should be logged with comprehensive details including:
   - The specific operation that failed
   - All relevant parameters and context
   - The complete error message and stack trace
   - Any system state information that might be relevant

2. **Fail Fast and Explicitly**: When critical operations fail (like OpenAI API calls), the system should:
   - Raise appropriate exceptions rather than falling back to default values
   - Propagate errors to the appropriate level where they can be handled meaningfully
   - Provide clear error messages that help identify the root cause

3. **Monitoring Over Masking**: Instead of hiding errors with fallbacks:
   - Implement robust monitoring to detect and alert on failures
   - Create dashboards to track error rates and types
   - Set up alerting for critical failures that require immediate attention

4. **Graceful Degradation vs. Silent Fallbacks**: When alternative behavior is necessary:
   - Clearly log that the primary approach failed and a secondary approach is being used
   - Ensure the degraded functionality is obvious to users and operators
   - Track these occurrences as incidents requiring investigation, not as normal operation

This approach ensures that real problems are visible and fixable, rather than being masked by fallback mechanisms that create subtle, hard-to-diagnose issues.

### Example: Influence Music Processing

The `process_influence_music` function should be modified to remove silent fallbacks with default lyrics. Instead, it should:

1. Log detailed errors when OpenAI fails to generate parameters
2. Provide specific error messages that help diagnose the issue
3. Either retry with different parameters or fail explicitly
4. Never use generic default lyrics that mask the real problem
