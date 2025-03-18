#!/usr/bin/env python
"""
Test Environment Variables Script

This script tests if the environment variables are correctly loaded.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config import MUSICAPI_KEY, OPENAI_KEY, SUPABASE_URL, SUPABASE_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to test environment variables."""
    # Load environment variables
    load_dotenv()
    
    logger.info("Testing environment variables...")
    
    # Check if environment variables are accessible
    logger.info(f"MUSICAPI_KEY exists: {bool(MUSICAPI_KEY)}")
    if MUSICAPI_KEY:
        logger.info(f"MUSICAPI_KEY first 5 chars: {MUSICAPI_KEY[:5]}...")
    
    logger.info(f"OPENAI_KEY exists: {bool(OPENAI_KEY)}")
    if OPENAI_KEY:
        logger.info(f"OPENAI_KEY first 5 chars: {OPENAI_KEY[:5]}...")
    
    logger.info(f"SUPABASE_URL exists: {bool(SUPABASE_URL)}")
    if SUPABASE_URL:
        logger.info(f"SUPABASE_URL: {SUPABASE_URL}")
    
    logger.info(f"SUPABASE_KEY exists: {bool(SUPABASE_KEY)}")
    if SUPABASE_KEY:
        logger.info(f"SUPABASE_KEY first 5 chars: {SUPABASE_KEY[:5]}...")
    
    # Direct access through os.environ
    logger.info("\nAccessing from os.environ directly:")
    logger.info(f"MUSICAPI_KEY exists: {bool(os.getenv('MUSICAPI_KEY'))}")
    if os.getenv('MUSICAPI_KEY'):
        logger.info(f"MUSICAPI_KEY first 5 chars: {os.getenv('MUSICAPI_KEY')[:5]}...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 