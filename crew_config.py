#!/usr/bin/env python
"""
CrewAI Configuration Module

This module loads environment variables and provides configuration for the CrewAI integration.
"""
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Keys
OPENAI_KEY = os.getenv('OPENAI_KEY')
MUSICAPI_KEY = os.getenv('MUSICAPI_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Validate required environment variables
if not all([OPENAI_KEY, MUSICAPI_KEY, SUPABASE_URL, SUPABASE_KEY]):
    missing = []
    if not OPENAI_KEY: missing.append("OPENAI_KEY")
    if not MUSICAPI_KEY: missing.append("MUSICAPI_KEY")
    if not SUPABASE_URL: missing.append("SUPABASE_URL")
    if not SUPABASE_KEY: missing.append("SUPABASE_KEY")
    logger.error(f"Missing required environment variables: {', '.join(missing)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

logger.info("Environment variables loaded successfully")
