# Yona AI K-pop Star System

An agentic AI K-pop star system that creates music using MusicAPI.ai and stores song data in Supabase.

## Features

- Creates K-pop songs via MusicAPI.ai
- Stores song creation inputs and outputs in Supabase
- Supports various song generation parameters
- Includes utilities for creating similar songs based on previous ones

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   MUSICAPI_KEY=your_musicapi_key
   OPENAI_KEY=your_openai_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

## Usage

### Creating a Song

```bash
python src/create_song.py --title "Song Title" --lyrics-file lyrics/your_lyrics.txt --style "kpop, electronic" --mv "sonic-v4"
```

### Creating a Similar Song

```bash
python src/create_similar_song.py --reference "song_id" --title "New Title" --lyrics "New lyrics"
```

### Listing Songs

```bash
python src/list_songs.py
```

## Project Structure

- `src/`: Source code
  - `main.py`: Main entry point
  - `music_api.py`: MusicAPI.ai integration
  - `create_song.py`: Script for creating songs
  - `create_similar_song.py`: Script for creating similar songs
  - `list_songs.py`: Script for listing songs
- `lyrics/`: Lyrics files
- `config/`: Configuration files

## Note

This project uses MusicAPI.ai for song generation. You'll need a valid API key to use the real API endpoints.

## Current Status

- **MusicAPI.ai Integration**: Updated to match the latest API documentation. The persona creation feature is currently unstable according to MusicAPI.ai support, so the system is configured to use direct song generation.
- **OpenAI Integration**: Running in simulation mode to save API costs.
- **Supabase Integration**: Ready for storing song data.

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   # MusicAPI/Suno API Key
   MUSICAPI_KEY=your_api_key_here
   
   # OpenAI API Key
   OPENAI_KEY=your_openai_key_here
   
   # Supabase Credentials
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_key_here
   ```
4. Run the application:
   ```
   python src/main.py
   ```

## Project Structure

- `src/`: Source code
  - `main.py`: Main application entry point
  - `music_api.py`: MusicAPI.ai client
  - `supabase_client.py`: Supabase client
- `config/`: Configuration files
- `tests/`: Test files

## API Integration Notes

### MusicAPI.ai

The MusicAPI.ai integration has been updated to match the latest API documentation:

1. **Song Creation Process**:
   - Send a POST request to `https://api.musicapi.ai/api/v1/sonic/create` with song details
   - Receive a `task_id` for the song generation task
   - Poll the status endpoint `https://api.musicapi.ai/api/v1/sonic/music?task_id={task_id}` until the song is ready

2. **Required Parameters**:
   - `custom_mode`: Set to `true` for custom lyrics
   - `prompt`: Song lyrics or description (< 3000 characters)
   - `mv`: Music model to use (`sonic-v3-5` or `sonic-v4`)

3. **Optional Parameters**:
   - `title`: Song title (< 80 characters)
   - `tags`: Music style/genre
   - `negative_tags`: Elements to avoid in the song
   - `make_instrumental`: Whether to create an instrumental version

**Important**: If you're experiencing issues with the MusicAPI.ai API, please note:
1. The persona creation endpoint is currently unstable according to MusicAPI.ai support
2. Make sure your API key is valid and not expired
3. The API key should be provided as a Bearer token in the Authorization header

### OpenAI

The OpenAI integration is configured to run in simulation mode to save API costs. To use the real API:
1. Ensure you have a valid OpenAI API key in your `.env` file
2. Set `SIMULATE_OPENAI = False` in `src/main.py`

### Supabase

The Supabase integration is ready for storing song data. To use the real API:
1. Ensure you have valid Supabase credentials in your `.env` file
2. Initialize the SupabaseClient with `simulation_mode=False`

## Troubleshooting

If you encounter issues with the MusicAPI.ai API:
1. Check if your API key is valid and not expired
2. Ensure you're using the correct API endpoints and parameters
3. Be aware that the persona creation feature is currently unstable
4. Contact MusicAPI.ai support if issues persist

## License

This project is licensed under the MIT License - see the LICENSE file for details. 