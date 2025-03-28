#!/usr/bin/env python
"""
Yona CLI - Command Line Interface for Yona

This script provides a simple command-line interface for interacting with Yona,
an agentic AI K-pop star. It allows users to send natural language requests to
Yona and receive responses.
"""
import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import YonaAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Interact with Yona, an agentic AI K-pop star')
    
    # Optional arguments
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--request', help='Single request to process (non-interactive mode)')
    
    return parser.parse_args()

def print_welcome_message():
    """Print a welcome message for the Yona CLI."""
    print("\n" + "=" * 50)
    print("Welcome to Yona CLI!")
    print("Yona is an agentic AI K-pop star that can create songs for you.")
    print("=" * 50)
    print("\nYou can ask Yona to:")
    print("- Create a song (e.g., 'Create a song about friendship')")
    print("- List your songs (e.g., 'List all my songs')")
    print("- Get a specific song (e.g., 'Get song with ID 123')")
    print("\nType 'exit' or 'quit' to end the session.")
    print("=" * 50 + "\n")

def interactive_mode(agent):
    """
    Run the CLI in interactive mode, allowing multiple requests.
    
    Args:
        agent: The YonaAgent instance to use for processing requests
    """
    print_welcome_message()
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check if the user wants to exit
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nThank you for using Yona CLI. Goodbye!")
            break
        
        # Process the request
        try:
            result = agent.process_user_request(user_input)
            
            # Print the response
            print(f"\nYona: {result['response']}")
            
            # If there's a result with audio_url, print it
            if result.get('result') and isinstance(result['result'], dict) and 'audio_url' in result['result']:
                print(f"\nAudio URL: {result['result']['audio_url']}")
                
            # If there's a result with video_url, print it
            if result.get('result') and isinstance(result['result'], dict) and 'video_url' in result['result']:
                print(f"Video URL: {result['result']['video_url']}")
                
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            print(f"\nYona: I'm sorry, I encountered an error while processing your request: {str(e)}")

def single_request_mode(agent, request):
    """
    Process a single request and exit.
    
    Args:
        agent: The YonaAgent instance to use for processing the request
        request: The request to process
    """
    try:
        result = agent.process_user_request(request)
        
        # Print the response
        print(f"\nYona: {result['response']}")
        
        # If there's a result with audio_url, print it
        if result.get('result') and isinstance(result['result'], dict) and 'audio_url' in result['result']:
            print(f"\nAudio URL: {result['result']['audio_url']}")
            
        # If there's a result with video_url, print it
        if result.get('result') and isinstance(result['result'], dict) and 'video_url' in result['result']:
            print(f"Video URL: {result['result']['video_url']}")
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        print(f"\nYona: I'm sorry, I encountered an error while processing your request: {str(e)}")

def main():
    """Main function to run the Yona CLI."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    # Initialize the agent
    logger.info("Initializing YonaAgent")
    agent = YonaAgent()
    
    # Test logging to Supabase
    logger.info("Test log message from Yona CLI")
    logger.warning("Test warning message from Yona CLI")
    logger.error("Test error message from Yona CLI")
    
    # Run in the appropriate mode
    if args.interactive:
        interactive_mode(agent)
    elif args.request:
        single_request_mode(agent, args.request)
    else:
        print("Please specify either --interactive or --request. Use --help for more information.")

if __name__ == "__main__":
    main()
