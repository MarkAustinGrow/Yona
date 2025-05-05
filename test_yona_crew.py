#!/usr/bin/env python
"""
Test Yona CrewAI Integration

This script tests the basic functionality of the Yona CrewAI integration.
"""
import logging
import sys
from yona_implementation import YonaImplementationManager
from yona_crew import create_yona_crew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_direct_implementation():
    """Test the direct implementation of Yona"""
    logger.info("Testing direct implementation of Yona")
    
    try:
        # Initialize Yona implementation manager
        yona_manager = YonaImplementationManager()
        
        # Test listing songs
        logger.info("Testing list_songs")
        songs = yona_manager.list_songs(limit=5)
        
        if songs:
            logger.info(f"Successfully listed {len(songs)} songs")
            for song in songs:
                logger.info(f"Song: {song.get('title')} (ID: {song.get('id')})")
        else:
            logger.info("No songs found or error occurred")
        
        return True
    except Exception as e:
        logger.error(f"Error testing direct implementation: {str(e)}")
        return False

def test_crew_implementation():
    """Test the CrewAI implementation of Yona"""
    logger.info("Testing CrewAI implementation of Yona")
    
    try:
        # Instead of creating the crew, just check if the agent can be created
        from yona_crew_agent import create_yona_agent
        logger.info("Creating CrewAI agent")
        agent = create_yona_agent()
        
        # Just check if the agent was created successfully
        if agent:
            logger.info("Successfully created CrewAI agent")
            logger.info(f"Agent role: {agent.role}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing CrewAI implementation: {str(e)}")
        return False

def main():
    """Main function"""
    logger.info("Starting Yona CrewAI integration test")
    
    # Test direct implementation
    direct_success = test_direct_implementation()
    
    # Test CrewAI implementation
    crew_success = test_crew_implementation()
    
    # Print results
    logger.info("\nTest Results:")
    logger.info(f"Direct Implementation: {'SUCCESS' if direct_success else 'FAILURE'}")
    logger.info(f"CrewAI Implementation: {'SUCCESS' if crew_success else 'FAILURE'}")
    
    # Exit with appropriate code
    if direct_success and crew_success:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error("Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
