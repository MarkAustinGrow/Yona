# Yona CrewAI Integration

This directory contains the integration of Yona AI with CrewAI, enabling Yona to be used as an agent within the CrewAI framework.

## Setup

1. Install the required dependencies:

```bash
pip install -r crewai_requirements.txt
```

2. Create a `.env` file with your API keys:

```bash
OPENAI_KEY=your_openai_key
MUSICAPI_KEY=your_musicapi_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Files

- `crew_config.py`: Loads environment variables and provides configuration
- `yona_implementation.py`: Manages the Yona implementation and provides methods to access its functionality
- `yona_tools.py`: Defines the CrewAI tools that expose Yona's functionality
- `yona_crew_agent.py`: Defines the CrewAI Agent with the Yona tools
- `yona_crew_tasks.py`: Defines the CrewAI Tasks that Yona will perform
- `yona_crew.py`: Sets up the CrewAI Crew with the Yona agent and tasks
- `yona_crew_cli.py`: Provides a command-line interface for executing Yona tasks through CrewAI
- `test_yona_crew.py`: Tests the basic functionality of the Yona CrewAI integration

## Usage

### Command-Line Interface

The `yona_crew_cli.py` script provides a command-line interface for executing Yona tasks through CrewAI.

#### Interactive Mode

```bash
python yona_crew_cli.py --interactive
```

This will start an interactive session where you can enter commands to execute Yona tasks.

#### Create a Song

```bash
python yona_crew_cli.py --task create_song --prompt "Create a happy K-pop song about summer adventures"
```

Additional parameters:
- `--api`: API to use ('sonic' or 'nuro')
- `--style`: Style tags for the song
- `--negative-tags`: Negative tags to avoid
- `--make-instrumental`: Make the song instrumental
- `--mv`: Music video generation type
- `--description`: Description prompt

Nuro-specific parameters:
- `--gender`: Singer gender ('Female' or 'Male')
- `--genre`: Genre of the song
- `--mood`: Mood of the song
- `--timbre`: Timbre of the song
- `--duration`: Duration in seconds

#### Process Feedback

```bash
python yona_crew_cli.py --task process_feedback --song-id "song_id" --feedback-id "feedback_id"
```

#### List Songs

```bash
python yona_crew_cli.py --task list_songs --limit 10 --offset 0
```

#### Process a Natural Language Request

```bash
python yona_crew_cli.py --task process_request --request "Create a song about friendship"
```

### Using CrewAI

To use CrewAI to execute tasks, add the `--use-crew` flag to any command:

```bash
python yona_crew_cli.py --task create_song --prompt "Create a happy K-pop song about summer adventures" --use-crew
```

### Programmatic Usage

You can also use the Yona CrewAI integration programmatically in your own Python code:

```python
from yona_crew import create_yona_crew

# Create the crew
crew = create_yona_crew()

# Execute a task
result = crew.kickoff()
print(result)
```

Or use the Yona implementation directly:

```python
from yona_implementation import YonaImplementationManager

# Initialize Yona implementation manager
yona_manager = YonaImplementationManager()

# Create a song
song = yona_manager.generate_song("Create a happy K-pop song about summer adventures")
print(song)
```

## Testing

To test the Yona CrewAI integration, run:

```bash
python test_yona_crew.py
```

This will test both the direct implementation and the CrewAI implementation of Yona.

## Customization

You can customize the Yona CrewAI integration by modifying the following files:

- `yona_implementation.py`: Add or modify methods to expose additional Yona functionality
- `yona_tools.py`: Add or modify tools to expose additional Yona functionality to CrewAI
- `yona_crew_tasks.py`: Add or modify tasks to define new workflows for Yona

## Troubleshooting

If you encounter any issues, check the following:

1. Make sure all required environment variables are set in the `.env` file
2. Check that all dependencies are installed correctly
3. Look for error messages in the logs
4. Try running the test script to verify that the integration is working correctly

If you still have issues, please open an issue on the GitHub repository.
