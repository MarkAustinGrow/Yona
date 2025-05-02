"""
Coral DID Integration

This module provides DID (Decentralized Identifier) integration for the Coral Protocol,
ensuring secure identity verification between agents.
"""
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoralDID:
    """
    DID integration for Coral Protocol.
    
    This class provides methods for secure identity verification using
    the existing DID system.
    """
    
    def __init__(self, did_manager):
        """
        Initialize CoralDID.
        
        Args:
            did_manager: DID manager instance
        """
        self.did_manager = did_manager
        logger.info(f"CoralDID initialized with DID: {self.did_manager.did}")
    
    def verify_agent_identity(self, agent_id: str, signature: str, message: str) -> bool:
        """
        Verify an agent's identity using their DID.
        
        Args:
            agent_id: Agent ID (usually contains or is derived from a DID)
            signature: Signature to verify
            message: Original message that was signed
            
        Returns:
            True if the signature is valid, False otherwise
        """
        try:
            # Extract DID from agent_id if it's in the format "did:web:example.com"
            # or use the agent_id directly if it's already a DID
            if agent_id.startswith("did:"):
                did = agent_id
            else:
                # Try to extract DID from agent_id (e.g., "yona_12345" -> get DID from our records)
                # This is a simplified example; in practice, you'd need a more robust way to map agent_ids to DIDs
                did = agent_id.split('_')[0] if '_' in agent_id else agent_id
            
            # Verify the signature using the DID manager
            is_valid = self.did_manager.verify_signature(did, signature, message)
            
            if is_valid:
                logger.info(f"Successfully verified signature from agent: {agent_id}")
            else:
                logger.warning(f"Failed to verify signature from agent: {agent_id}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying agent identity: {str(e)}")
            return False
    
    def sign_message(self, message: str) -> Dict[str, str]:
        """
        Sign a message using the agent's DID.
        
        Args:
            message: Message to sign
            
        Returns:
            Dictionary containing the signature and DID
        """
        try:
            # Sign the message using the DID manager
            signature = self.did_manager.sign(message)
            
            return {
                "did": self.did_manager.did,
                "signature": signature,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error signing message: {str(e)}")
            return {
                "did": self.did_manager.did,
                "error": str(e)
            }
    
    def get_auth_headers(self, request_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Get authentication headers for a request.
        
        Args:
            request_data: Optional data to include in the signature
            
        Returns:
            Dictionary with authentication headers
        """
        return self.did_manager.get_auth_headers(request_data)
