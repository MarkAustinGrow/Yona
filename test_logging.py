#!/usr/bin/env python
"""
Test script for the SupabaseLogHandler.

This script tests the SupabaseLogHandler by logging a test message
to the Supabase yona_logs table.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.supabase_client import SupabaseClient
from src.logging_utils import SupabaseLogHandler

def main():
    """Test the SupabaseLogHandler."""
    # Load environment variables
    load_dotenv()
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("test_logging")
    
    # Initialize Supabase client
    try:
        supabase_client = SupabaseClient()
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        return 1
    
    # Add Supabase log handler
    try:
        supabase_handler = SupabaseLogHandler(supabase_client)
        supabase_handler.setLevel(logging.INFO)
        supabase_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(supabase_handler)
        print("Supabase log handler added to logger")
    except Exception as e:
        print(f"Error adding Supabase log handler: {str(e)}")
        return 1
    
    # Log a test message
    try:
        logger.info("This is a test log message from test_logging.py")
        print("Test log message sent to Supabase")
    except Exception as e:
        print(f"Error logging test message: {str(e)}")
        return 1
    
    print("Test completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
