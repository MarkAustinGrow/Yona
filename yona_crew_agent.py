#!/usr/bin/env python
"""
Yona CrewAI Agent

This module defines the CrewAI Agent with the Yona tools.
"""
import logging
from crewai import Agent
from yona_tools import get_yona_tools
from crew_config import OPENAI_KEY

logger = logging.getLogger(__name__)

def create_yona_agent() -> Agent:
    """
    Create a CrewAI Agent for Yona
    
    Returns:
        CrewAI Agent object
    """
    logger.info("Creating Yona CrewAI Agent")
    
    # Get the tools that expose Yona's functionality
    tools = get_yona_tools()
    
    # Create the CrewAI Agent
    yona_agent = Agent(
        role='AI Music Creator',
        goal='Generate music based on prompts, lyrics, feedback, or influences.',
        backstory="""
        Yona is an AI-powered music agent specializing in generating K-pop songs and managing 
        feedback-driven iterations. Yona can create songs from prompts, process feedback to 
        improve songs, and manage a database of created songs. Yona also supports decentralized 
        identity (DID) and the Model Context Protocol (MCP) for secure, authenticated communication.
        """,
        tools=tools,
        verbose=True,
        llm_config={
            "api_key": OPENAI_KEY,
            "model": "gpt-4o"
        }
    )
    
    logger.info("Yona CrewAI Agent created successfully")
    return yona_agent
