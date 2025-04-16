# Yona: Current Build Specifications

## 1. Overview

Yona is an AI music creation platform that allows users to generate music based on text prompts and feedback. The system integrates with multiple music generation APIs and provides a RESTful API for client applications to interact with the service.

**Current Version:** 0.1.0  
**Deployment Status:** Production (Deployed on Linode server at yona.club)  
**Last Updated:** April 2025

## 2. Core Capabilities

### 2.1 Song Generation
- Text-to-music generation using either Sonic or Nuro APIs
- Support for various musical styles, moods, and genres
- Ability to specify voice gender, instrumentation, and other parameters
- Music video generation with multiple visualization options
- Automatic parameter optimization based on user prompts

### 2.2 Feedback Processing
- Automated processing of user feedback to improve songs
- Intelligent parameter modification using OpenAI
- Song versioning system to track changes and improvements
- Rating system for feedback prioritization

### 2.3 Influence Music Processing
- Creation of songs inspired by existing music
- Automatic analysis of musical characteristics (BPM, key, moods)
- Parameter optimization based on musical analysis
- Intelligent mapping of musical characteristics to generation parameters

### 2.4 MCP Implementation
- Decentralized identity (DID) management for secure agent communication
- Capability document generation for service discovery
- Authenticated API requests using DID signatures
- Standardized protocol for AI agent interactions

## 3. API Integrations

### 3.1 Sonic API
**Capabilities:**
- Full song generation from text prompts
- Music video generation
- Style-based generation with tags

**Parameters:**
- `prompt`: Lyrics or text prompt for the song
- `title`: Song title
- `style`: Style tags (e.g., "pop, upbeat, summer")
- `negative_tags`: Tags to avoid in generation
- `make_instrumental`: Boolean for instrumental versions
- `mv`: Music video generation type (sonic-v3-5 or sonic-v4)
- `gpt_description_prompt`: Additional description for guiding generation
- `voice_gender`: Gender of the singer's voice (female or male)

### 3.2 Nuro API
**Capabilities:**
- Lyrics-to-song generation
- Fine-grained control over musical parameters
- Consistent voice characteristics

**Parameters:**
- `lyrics`: Lyrics for the song (max 2000 characters)
- `gender`: Singer's gender (Female or Male)
- `genre`: Genre of the song (Pop, Rock, Folk, etc.)
- `mood`: Mood of the song (Happy, Sad, Energetic, etc.)
- `timbre`: Timbre of the singer's voice (Warm, Bright, Husky, etc.)
- `duration`: Duration in seconds (30-240)

### 3.3 Automatic Fallback Mechanism
- Automatic detection of Sonic API maintenance status
- Seamless fallback to Nuro API when Sonic API is unavailable
- Intelligent parameter mapping between APIs
- Transparent logging of API switches

## 4. User Interfaces

### 4.1 Command-Line Tools
- `create_song.py`: Direct song creation with specified parameters
- `generate_song.py`: AI-assisted song generation from concept prompts
- `list_songs.py`: List songs stored in the database
- `yona_cli.py`: Interactive CLI for natural language requests
- `create_song_from_feedback.py`: Process specific feedback for a song
- `continuous_feedback_processor.py`: Daemon for automatic feedback processing

### 4.2 API Endpoints
- `/capabilities`: Serves the capability document
- `/.well-known/did.json`: Serves the DID document
- `/health`: Health check endpoint

### 4.3 Web Interface
- Currently not implemented in this build
- Planned for future releases

## 5. Database Schema

### 5.1 Songs Table
Stores the main song data including:
- `id`: UUID primary key
- `title`: Song title
- `persona_id`: Reference to persona ID (typically 'direct_generation')
- `lyrics`: Full lyrics of the song
- `audio_url`: URL to the generated audio
- `video_url`: URL to the generated video
- `image_url`: URL to the generated image
- `style`: Style tags for the song
- `make_instrumental`: Boolean flag for instrumental versions
- `mv`: Music video generation type
- `gpt_description`: Description prompt used
- `negative_tags`: Tags to avoid in generation
- `duration`: Duration of the song in seconds
- `params_used`: JSON object with all parameters used
- `processor_did`: DID of the agent that processed the song
- `original_song_id`: Reference to the original song (for songs created from feedback)
- `feedback_id`: Reference to the feedback that prompted this song
- `api_used`: Which API was used to generate the song

### 5.2 Feedback Table
Stores user feedback on songs:
- `id`: UUID primary key
- `song_id`: Reference to the song being commented on
- `comments`: User feedback comments
- `rating`: Rating value (NULL indicates unprocessed feedback)
- `created_at`: Timestamp of creation

### 5.3 Song Versions Table
Tracks the evolution of songs through versions:
- `id`: UUID primary key
- `song_id`: Reference to the original song
- `version_number`: Sequential version number
- `title`: Title of this version
- `lyrics`: Lyrics for this version
- `audio_url`: URL to the generated audio
- `params_used`: Parameters used for this version
- `created_at`: Timestamp of creation

### 5.4 Influence Music Table
Stores reference music for inspiration:
- `id`: UUID primary key
- `url`: URL to the reference music
- `analysis`: JSON data including BPM, key, and moods
- `song_id`: Reference to the song created from this influence (NULL indicates unprocessed)
- `created_at`: Timestamp of creation

### 5.5 Yona Logs Table
Stores application logs:
- `id`: UUID primary key
- `timestamp`: When the log was created
- `level`: Log level (INFO, WARNING, ERROR, etc.)
- `message`: Log message
- `container`: Source container or component
- `metadata`: Additional JSON metadata

## 6. Deployment Specifications

### 6.1 Docker Configuration
- Two services defined in docker-compose.yml:
  - `yona-api`: Runs the API server on port 5000
  - `yona-feedback-processor`: Runs the continuous feedback processor
- Base image: Python 3.9
- Exposed ports: 5000 (API)
- Volume mounts: logs/ directory

### 6.2 Server Requirements
- **Hosting:** Linode server
- **IP Address:** 172-236-28-244
- **Domain:** yona.club
- **Operating System:** Ubuntu 22.04 LTS
- **Minimum Specs:** 2GB RAM, 2 vCPUs, 50GB SSD
- **Nginx:** Configured as reverse proxy with SSL

### 6.3 Environment Variables
Required environment variables:
- `OPENAI_KEY`: API key for OpenAI
- `MUSICAPI_KEY`: API key for MusicAPI.ai
- `SUPABASE_URL`: URL for Supabase database
- `SUPABASE_KEY`: API key for Supabase
- `YOUTUBE_API_KEY`: API key for YouTube (optional)
- `YOUTUBE_CLIENT_ID`: Client ID for YouTube API (optional)
- `YOUTUBE_CLIENT_SECRET`: Client secret for YouTube API (optional)

## 7. Current Limitations

### 7.1 Known Issues
- Persona creation is currently unstable according to MusicAPI support
- Song creation may time out for complex requests
- Nuro API has a 2000 character limit for lyrics
- Limited error handling for API rate limits

### 7.2 Performance Constraints
- Feedback processing is limited to one record per hour to manage API usage
- Song generation typically takes 1-3 minutes depending on length
- Music video generation adds significant processing time
- Maximum song duration is limited to 4 minutes (240 seconds)

## 8. Recent Improvements

### 8.1 Latest Features Added
- Support for Nuro API integration
- Automatic fallback mechanism between APIs
- Influence music processing system
- DID-based authentication for API requests
- Improved logging with Supabase integration

### 8.2 Recent Bug Fixes
- Fixed database schema compatibility issue with clip_id field
- Increased song creation timeout from 30 to 60 attempts
- Added check_interval parameter for status polling
- Fixed continuous feedback processor syntax error
- Improved error handling for API maintenance scenarios
- Added timezone handling for log timestamps

---

*This document reflects the current build as of April 2025 and is subject to change as development continues.*
