# Yona - Agentic AI K-pop Star

Yona is an agentic AI K-pop star system that can create songs, generate lyrics, and interact with users through natural language. It uses OpenAI for decision-making, MusicAPI.ai for song creation, and Supabase for data storage.

## Features

- **Song Creation**: Create K-pop songs with custom lyrics and styles
- **AI-Generated Lyrics**: Generate lyrics based on concepts or themes
- **Agentic Interaction**: Interact with Yona using natural language
- **Database Storage**: Store and retrieve songs from Supabase

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- MusicAPI.ai API key
- Supabase account and API keys

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd yona-cline
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your API keys:
   ```
   OPENAI_KEY=your_openai_api_key
   MUSICAPI_KEY=your_musicapi_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

## Usage

### Creating a Song with Lyrics

```bash
python src/create_song.py --title "My Song Title" --lyrics-file lyrics/my_lyrics.txt --style "kpop, electronic"
```

### Generating a Song from a Concept

```bash
python src/generate_song.py "Create an upbeat song about friendship and summer adventures"
```

### Interactive Mode

```bash
python src/yona_cli.py --interactive
```

This will start an interactive session where you can talk to Yona directly:

```
=================================================
Welcome to Yona CLI!
Yona is an agentic AI K-pop star that can create songs for you.
=================================================

You can ask Yona to:
- Create a song (e.g., 'Create a song about friendship')
- List your songs (e.g., 'List all my songs')
- Get a specific song (e.g., 'Get song with ID 123')

Type 'exit' or 'quit' to end the session.
=================================================

You: Create a song about skateboarding in the city
```

### Single Request Mode

```bash
python src/yona_cli.py --request "Create a song about the ocean"
```

### Simulation Mode

For testing without making API calls:

```bash
python src/yona_cli.py --interactive --simulation
```

## Project Structure

- `src/`: Main source code
  - `agent.py`: YonaAgent implementation
  - `music_api.py`: MusicAPI client
  - `supabase_client.py`: Supabase client
  - `create_song.py`: Script for creating songs with provided lyrics
  - `generate_song.py`: Script for generating and creating songs
  - `list_songs.py`: Script for listing songs
  - `yona_cli.py`: Interactive CLI for Yona
  - `config/`: Configuration files
- `tests/`: Test files
- `lyrics/`: Example lyrics files

## Testing

Run the tests with:

```bash
python -m unittest discover tests
```

## License

[MIT License](LICENSE)
