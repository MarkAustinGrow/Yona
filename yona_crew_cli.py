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
from yona_crew import create_yona_crew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def output_result(result, output_format='text'):
    """
    Output the result in the specified format
    
    Args:
        result: The result to output
        output_format: The format to output the result in ('text' or 'json')
    """
    if output_format == 'json':
        print(json.dumps(result, indent=2))
    else:
        if isinstance(result, list):
            for item in result:
                print(f"ID: {item.get('id')}")
                print(f"Title: {item.get('title')}")
                print(f"Audio URL: {item.get('audio_url')}")
                print(f"Video URL: {item.get('video_url')}")
                print(f"Image URL: {item.get('image_url')}")
                print("-" * 50)
        elif isinstance(result, dict):
            if result.get('status') == 'failed':
                print(f"Error: {result.get('error')}")
            else:
                print(f"ID: {result.get('id')}")
                print(f"Title: {result.get('title')}")
                print(f"Audio URL: {result.get('audio_url')}")
                print(f"Video URL: {result.get('video_url')}")
                print(f"Image URL: {result.get('image_url')}")
                
                if 'response' in result:
                    print(f"\nResponse: {result.get('response')}")
        else:
            print(result)

def run_interactive_mode(yona_manager):
    """
    Run in interactive mode, allowing multiple requests
    
    Args:
        yona_manager: YonaImplementationManager instance
    """
    print("Welcome to Yona CrewAI CLI Interactive Mode")
    print("Type 'exit' or 'quit' to exit")
    print("Type 'help' for a list of commands")
    
    while True:
        try:
            user_input = input("\nYona> ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  create <prompt> - Create a song with the given prompt")
                print("  list [limit] [offset] - List songs from the database")
                print("  get <song_id> - Get a specific song by ID")
                print("  process <song_id> <feedback_id> - Process feedback for a song")
                print("  request <text> - Process a natural language request")
                print("  exit/quit - Exit the program")
                print("  help - Show this help message")
                continue
            
            if user_input.lower().startswith('create '):
                prompt = user_input[7:]
                print(f"Creating song with prompt: {prompt}")
                result = yona_manager.generate_song(prompt)
                output_result(result)
                
            elif user_input.lower().startswith('list'):
                parts = user_input.split()
                limit = 10
                offset = 0
                
                if len(parts) > 1 and parts[1].isdigit():
                    limit = int(parts[1])
                
                if len(parts) > 2 and parts[2].isdigit():
                    offset = int(parts[2])
                
                print(f"Listing songs (limit: {limit}, offset: {offset})")
                result = yona_manager.list_songs(limit, offset)
                output_result(result)
                
            elif user_input.lower().startswith('get '):
                song_id = user_input[4:]
                print(f"Getting song with ID: {song_id}")
                result = yona_manager.get_song(song_id)
                output_result(result)
                
            elif user_input.lower().startswith('process '):
                parts = user_input.split()
                if len(parts) < 3:
                    print("Error: process command requires song_id and feedback_id")
                    continue
                
                song_id = parts[1]
                feedback_id = parts[2]
                
                print(f"Processing feedback {feedback_id} for song {song_id}")
                result = yona_manager.process_feedback(song_id, feedback_id)
                output_result(result)
                
            elif user_input.lower().startswith('request '):
                request_text = user_input[8:]
                print(f"Processing request: {request_text}")
                result = yona_manager.process_user_request(request_text)
                output_result(result)
                
            else:
                print(f"Processing request: {user_input}")
                result = yona_manager.process_user_request(user_input)
                output_result(result)
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {str(e)}")

def run_crew_task(task_name, **kwargs):
    """
    Run a specific CrewAI task
    
    Args:
        task_name: Name of the task to run
        **kwargs: Additional parameters for the task
    """
    logger.info(f"Running CrewAI task: {task_name}")
    
    # Create the crew
    crew = create_yona_crew()
    
    # Get the task by name
    task = None
    for t in crew.tasks:
        if t.description.lower().startswith(task_name.lower()):
            task = t
            break
    
    if not task:
        logger.error(f"Task '{task_name}' not found")
        return {"status": "failed", "error": f"Task '{task_name}' not found"}
    
    # Execute the task
    logger.info(f"Executing task: {task.description}")
    result = task.execute(kwargs)
    
    return result

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
    parser.add_argument('--use-crew', action='store_true', help='Use CrewAI to execute tasks')
    
    args = parser.parse_args()
    
    # Initialize Yona implementation manager
    yona_manager = YonaImplementationManager()
    
    # Interactive mode
    if args.interactive:
        run_interactive_mode(yona_manager)
        return
    
    # Use CrewAI to execute tasks
    if args.use_crew:
        if args.task == 'create_song':
            if not args.prompt:
                logger.error("Prompt is required for create_song task")
                parser.print_help()
                sys.exit(1)
            
            result = run_crew_task('Generate and produce a song', prompt=args.prompt)
            output_result(result, args.output)
            return
        
        elif args.task == 'process_feedback':
            if not args.song_id or not args.feedback_id:
                logger.error("Song ID and feedback ID are required for process_feedback task")
                parser.print_help()
                sys.exit(1)
            
            result = run_crew_task('Process user feedback', song_id=args.song_id, feedback_id=args.feedback_id)
            output_result(result, args.output)
            return
        
        elif args.task == 'list_songs':
            result = run_crew_task('List songs', limit=args.limit, offset=args.offset)
            output_result(result, args.output)
            return
        
        elif args.task == 'process_request':
            if not args.request:
                logger.error("Request is required for process_request task")
                parser.print_help()
                sys.exit(1)
            
            result = run_crew_task('Process a natural language request', user_input=args.request)
            output_result(result, args.output)
            return
    
    # Execute the specified task directly
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

if __name__ == "__main__":
    main()
