# Yona Codebase Documentation

## 1. Project Structure

The project is structured as follows:

- `src/`: Main source code directory
  - `config/`: Configuration files
  - `examples/`: Example scripts
  - `migrations/`: Database migration scripts
  - Multiple Python modules for different functionalities
- `lyrics/`: Directory containing lyrics files for song creation
- `tests/`: Test files for the project

## 2. Dependencies and Imports

### Core Dependencies
- Python standard libraries: `os`, `sys`, `time`, `json`, `logging`, `argparse`, `tempfile`
- External libraries:
  - `dotenv`: Environment variable management
  - `httpx`: HTTP client for API calls
  - `supabase`: Supabase client for database operations
  - `openai`: OpenAI API client

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
from src.config.config import MUSICAPI_KEY, MUSICAPI_BASE_URL
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
- `YONA_PERSONA`: Dictionary defining Yona's personality and style
- `DEFAULT_SONG_PARAMETERS`: Default parameters for song creation

## 4. Database Schema

Based on the code analysis, the Supabase database schema includes a `songs` table with the following structure:

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

## 5. Key Classes and Methods

### YonaAgent (src/agent.py)

```python
class YonaAgent:
    def __init__(self, openai_api_key=None, simulation_mode=False)
    def generate_song_concept(self, prompt)
    def generate_lyrics(self, concept)
    def create_song(self, title, lyrics, style=None, negative_tags=None, make_instrumental=False,
                   mv='sonic-v4', gpt_description_prompt=None, voice_gender='female', max_attempts=60,
                   check_interval=30)
    def list_songs(self, limit=10, offset=0)
    def process_user_request(self, user_input)
    def _analyze_request(self, user_input)
```

### MusicAPI (src/music_api.py)

```python
class MusicAPI:
    def __init__(self, api_key=None, base_url=None, simulation_mode=False)
    def create_song(self, prompt, title=None, style=None, negative_tags=None, make_instrumental=False, 
                   mv='sonic-v4', gpt_description_prompt=None, voice_gender='female')
    def check_song_status(self, task_id)
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
```

## 6. Command-line Scripts

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
- `--simulation`: Run in simulation mode (flag)

### generate_song.py

Generates a song concept and lyrics using AI, then creates the song.

Similar parameters to create_song.py, plus:
- `--prompt`: Concept prompt for generating the song idea

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

# Simulation mode (for testing without API calls)
python src/yona_cli.py --interactive --simulation
```

## 7. Integration Points

1. **OpenAI API Integration**:
   - Used in YonaAgent for generating song concepts and lyrics
   - Configured with the OPENAI_KEY from environment variables

2. **MusicAPI.ai Integration**:
   - Core integration for song creation, cover creation, and persona creation
   - Handles API requests, payload formatting, and response processing

3. **Supabase Integration**:
   - Used for storing song data, including metadata and generated URLs
   - Configured with SUPABASE_URL and SUPABASE_KEY from environment variables

## 8. Data Flow

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

## 9. Recently Fixed Issues

1. Database schema compatibility issue:
   - The code was attempting to store a `clip_id` field that didn't exist in the Supabase schema
   - Fixed by removing the `clip_id` field and adding `persona_id` with value 'direct_generation'
   - Changes made to both create_song.py and generate_song.py

2. Song creation timeout issue:
   - Increased max_attempts from 30 to 60
   - Added check_interval parameter (default: 30 seconds)
   - Improved error handling and logging
   - Added logic to consider a song successful if it has an audio URL even if status is still "pending"

## 10. Backup Recommendation

To prevent code damage during major changes:
1. Commit changes frequently with descriptive messages
2. Create Git branches for major features
3. Consider using Git tags to mark stable versions
4. Implement automated tests for core functionality
5. Document all environment variables and configurations
