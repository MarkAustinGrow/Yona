import logging
import requests
from coral_client import CoralClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coral_test")

def test_basic_connection():
    """Test basic connection to the Coral server."""
    server_url = "https://coral.pushcollective.club"
    logger.info(f"Testing basic connection to {server_url}")
    
    try:
        # Try a simple GET request to see if the server is reachable
        response = requests.get(f"{server_url}/health", timeout=10)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("Basic connection successful!")
            return True
        else:
            logger.info(f"Connection returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return False

def test_coral_client():
    """Test the Coral client connection."""
    logger.info("Testing Coral client connection...")
    
    try:
        # Create a client
        logger.info("Creating Coral client...")
        client = CoralClient(
            session_id="linode-test",
            server_url="https://coral.pushcollective.club",
            use_devmode=True
        )
        
        logger.info("Client initialized successfully!")
        
        # Try listing agents
        logger.info("Listing agents...")
        agents = client.list_agents()
        
        if agents:
            logger.info(f"Successfully retrieved {len(agents)} agents")
            for agent in agents:
                logger.info(f"- {agent.get('name', 'Unknown')} ({agent.get('agent_id', 'Unknown')})")
            return True
        else:
            logger.info("No agents found or failed to retrieve agents")
            return True  # Still consider successful if we got a response
        
    except Exception as e:
        logger.error(f"Coral client test failed: {str(e)}")
        return False

def test_register_agent():
    """Test registering an agent."""
    logger.info("Testing agent registration...")
    
    try:
        # Create a client
        client = CoralClient(
            session_id="linode-test-register",
            server_url="https://coral.pushcollective.club",
            use_devmode=True
        )
        
        # Register a test agent
        agent_id = client.register_agent(
            name="TestAgent",
            description="A test agent for the Coral Protocol"
        )
        
        if agent_id:
            logger.info(f"Successfully registered agent with ID: {agent_id}")
            return True
        else:
            logger.info("Failed to register agent")
            return False
            
    except Exception as e:
        logger.error(f"Agent registration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting Coral connection tests...")
    
    # Test basic connection
    if test_basic_connection():
        # Test Coral client
        if test_coral_client():
            # Test agent registration
            test_register_agent()
    
    logger.info("Tests completed.")
