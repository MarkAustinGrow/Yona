#!/usr/bin/env python
"""
Yona CrewAI Crew

This module sets up the CrewAI Crew with the Yona agent and tasks.
"""
import logging
from crewai import Crew
from yona_crew_agent import create_yona_agent
from yona_crew_tasks import create_yona_tasks

logger = logging.getLogger(__name__)

def create_yona_crew() -> Crew:
    """
    Create a CrewAI Crew with the Yona agent and tasks
    
    Returns:
        CrewAI Crew object
    """
    logger.info("Creating Yona CrewAI Crew")
    
    # Get the agent and tasks
    yona_agent = create_yona_agent()
    tasks = create_yona_tasks()
    
    # Create the crew
    crew = Crew(
        agents=[yona_agent],
        tasks=tasks,
        verbose=True
    )
    
    logger.info("Yona CrewAI Crew created successfully")
    return crew
