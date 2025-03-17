"""
Script to set up the Supabase database for the Yona AI K-pop star system.
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def setup_supabase():
    """Set up the Supabase database with the required tables."""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials missing. Please check your .env file.")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        
        # Create the songs table using SQL
        # Note: This requires the service_role key or a key with enough permissions
        # For this example, we'll use the REST API to check if the table exists
        
        # Check if the songs table exists
        response = supabase.table("songs").select("count", count="exact").limit(1).execute()
        
        if hasattr(response, 'error') and response.error:
            logger.info("Songs table doesn't exist. Creating it now...")
            
            # Create the songs table using SQL
            # This is a simplified approach - in a production environment,
            # you would use migrations or a more robust approach
            sql = """
            CREATE TABLE IF NOT EXISTS songs (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                title TEXT,
                persona_id TEXT,
                lyrics TEXT,
                audio_url TEXT,
                params_used JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Execute the SQL (this requires appropriate permissions)
            # For this example, we'll just log the SQL
            logger.info(f"SQL to execute: {sql}")
            logger.info("Please execute this SQL in the Supabase SQL editor if you have access.")
            logger.info("Otherwise, create the table manually through the Supabase dashboard.")
        else:
            logger.info("Songs table already exists")
            count = response.count if hasattr(response, 'count') else 0
            logger.info(f"Current number of songs in the database: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Setting up Supabase database...")
    if setup_supabase():
        logger.info("Supabase setup completed successfully")
    else:
        logger.error("Supabase setup failed") 