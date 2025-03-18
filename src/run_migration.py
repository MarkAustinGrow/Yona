"""
Script to run SQL migrations on the Supabase database.
"""
import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from supabase import create_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def run_migration(migration_file):
    """
    Run a SQL migration file on the Supabase database.
    
    Args:
        migration_file (str): Path to the SQL migration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials missing. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
        return False
    
    try:
        # Initialize Supabase client
        client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        
        # Read the SQL migration file
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Execute the SQL migration
        logger.info(f"Running migration: {migration_file}")
        
        # Split the SQL into individual statements
        statements = sql.split(';')
        
        # Execute each statement
        for statement in statements:
            # Skip empty statements
            if statement.strip():
                try:
                    # Execute the SQL statement using the rpc function
                    response = client.rpc('exec_sql', {'sql': statement}).execute()
                    
                    # Check if there was an error
                    if hasattr(response, 'error') and response.error:
                        logger.error(f"Error executing SQL statement: {response.error}")
                        return False
                    
                    logger.info(f"SQL statement executed successfully")
                except Exception as e:
                    logger.error(f"Error executing SQL statement: {str(e)}")
                    return False
        
        # Note about song_versions table
        logger.info("Note: The database has a song_versions table that may be used for tracking different versions of songs.")
        logger.info("The is_cover and original_clip_id fields added to the songs table provide a way to identify cover songs.")
        logger.info("Consider using both tables together for a complete version history of songs.")
        
        logger.info(f"Migration {migration_file} completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error running migration: {str(e)}")
        return False

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Run SQL migrations on the Supabase database')
    parser.add_argument('--migration-file', type=str, required=True, help='Path to the SQL migration file')
    
    args = parser.parse_args()
    
    # Check if the migration file exists
    if not os.path.isfile(args.migration_file):
        logger.error(f"Migration file not found: {args.migration_file}")
        sys.exit(1)
    
    # Run the migration
    success = run_migration(args.migration_file)
    
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 