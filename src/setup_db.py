"""
Script to set up the database schema in Supabase.
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv
from config.config import SUPABASE_URL, SUPABASE_KEY

load_dotenv()

async def setup_database():
    """Set up the database schema in Supabase."""
    print("Setting up database schema in Supabase...")
    
    # Check if credentials are available
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found. Please check your .env file.")
        return False
    
    # Read the schema file
    try:
        with open("schema.sql", "r") as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("Error: schema.sql file not found.")
        return False
    
    # Execute the SQL using the Supabase REST API
    try:
        # The Supabase REST API endpoint for SQL queries
        url = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql"
        
        # Headers for authentication
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        # Payload with the SQL to execute
        payload = {
            "query": schema_sql
        }
        
        # Make the request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                print("Database schema created successfully!")
                return True
            else:
                print(f"Error creating database schema: {response.text}")
                return False
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(setup_database()) 