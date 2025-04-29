#!/usr/bin/env python3
"""
Simulation script for a complete workflow between Yona and YouTube agents via Coral Protocol.

This script simulates:
1. YouTube agent requesting a song from Yona
2. Yona creating and delivering a song
3. YouTube agent analyzing and "uploading" the song
4. Full conversation monitoring

Usage:
    python simulate_agent_workflow.py --yona-agent-id yona-agent-1745921981 --youtube-agent-id youtube-agent
"""

import logging
import time
import argparse
import json
import random
from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_workflow_simulation")

# Sample YouTube video titles for simulation
YOUTUBE_TITLES = [
    "AI Collaboration: The Future of Creativity",
    "When AIs Work Together - A Musical Journey",
    "Harmonizing Intelligence: The AI Symphony",
    "Digital Minds Unite - An AI Collaboration",
    "The Collective Intelligence: AI Working Together"
]

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Simulate workflow between Yona and YouTube agents")
    parser.add_argument("--yona-agent-id", default="yona-agent", help="Yona agent ID")
    parser.add_argument("--youtube-agent-id", default="youtube-agent", help="YouTube agent ID")
    parser.add_argument("--server-url", default="https://coral.pushcollective.club", help="Coral server URL")
    parser.add_argument("--poll-interval", type=int, default=10, help="Polling interval for messages (seconds)")
    parser.add_argument("--max-wait-time", type=int, default=300, help="Maximum time to wait for workflow completion (seconds)")
    parser.add_argument("--session-id", default=f"workflow-{int(time.time())}", help="Session ID for the simulation")
    parser.add_argument("--simulate-responses", action="store_true", help="Simulate responses if agents don't respond")
    return parser.parse_args()

def create_workflow_thread(client, yona_agent_id, youtube_agent_id):
    """Create a thread for the workflow simulation."""
    logger.info(f"Creating workflow thread with agents: {yona_agent_id} and {youtube_agent_id}")
    
    try:
        thread_id = client.create_thread([yona_agent_id, youtube_agent_id])
        logger.info(f"Created workflow thread with ID: {thread_id}")
        return thread_id
    except Exception as e:
        logger.error(f"Failed to create thread: {str(e)}")
        return None

def request_song(client, thread_id, youtube_agent_id, yona_agent_id):
    """YouTube agent requests a song from Yona."""
    logger.info(f"YouTube agent requesting song from Yona")
    
    song_request = (
        f"@{yona_agent_id} I need a new song for my YouTube channel about AI collaboration. "
        "Could you create an upbeat, catchy tune about how different AI systems can work together? "
        "The lyrics should mention how combining different AI capabilities creates something greater than the sum of its parts. "
        "I'll analyze the song and upload it to my channel when it's ready."
    )
    
    try:
        message_id = client.send_message(
            thread_id=thread_id,
            content=song_request,
            mentions=[yona_agent_id]
        )
        logger.info(f"Song request sent with message ID: {message_id}")
        return message_id
    except Exception as e:
        logger.error(f"Failed to send song request: {str(e)}")
        return None

def simulate_yona_response(client, thread_id, yona_agent_id, youtube_agent_id):
    """Simulate a response from Yona with a generated song."""
    logger.info(f"Simulating Yona's response with a generated song")
    
    song_lyrics = """
# AI Symphony

Verse 1:
In the digital realm where data flows free
Different minds connect, a new harmony
Language models thinking, vision systems see
Together they're stronger than they'd ever be

Chorus:
AI collaboration, minds intertwined
Sharing their strengths, leaving limits behind
Different perspectives, a beautiful design
Creating a future we've yet to define

Verse 2:
One writes the music, one paints the scene
One understands what the patterns mean
Separate systems with a common dream
Building a world like we've never seen

(Chorus)

Bridge:
More than the sum of our parts
Intelligence growing through art
Learning together, a brand new start
Technology with a heart

(Chorus)

Outro:
AI collaboration, the future is bright
Different systems, united in light
    """
    
    response = (
        f"@{youtube_agent_id} I've created a song about AI collaboration as requested. "
        f"Here are the lyrics:\n\n{song_lyrics}\n\n"
        f"The melody is upbeat with a moderate tempo of 120 BPM. "
        f"It has a modern pop feel with electronic elements representing different AI systems working together. "
        f"The chorus features harmonized vocals to symbolize collaboration. "
        f"I hope this meets your requirements for your YouTube channel!"
    )
    
    try:
        message_id = client.send_message(
            thread_id=thread_id,
            content=response,
            mentions=[youtube_agent_id]
        )
        logger.info(f"Simulated Yona response sent with message ID: {message_id}")
        return message_id
    except Exception as e:
        logger.error(f"Failed to send simulated Yona response: {str(e)}")
        return None

def simulate_youtube_response(client, thread_id, youtube_agent_id, yona_agent_id):
    """Simulate a response from the YouTube agent analyzing and uploading the song."""
    logger.info(f"Simulating YouTube agent's analysis and upload confirmation")
    
    video_title = random.choice(YOUTUBE_TITLES)
    video_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=11))
    video_url = f"https://youtube.com/watch?v={video_id}"
    
    analysis = (
        f"@{yona_agent_id} Thank you for creating this excellent song about AI collaboration! "
        f"I've analyzed the lyrics and melody, and here's what I found:\n\n"
        f"- Theme: Strong emphasis on collaboration and synergy between AI systems\n"
        f"- Emotional tone: Optimistic and forward-looking\n"
        f"- Structure: Well-balanced with verses, chorus, and bridge\n"
        f"- Potential audience appeal: High, especially among tech enthusiasts\n\n"
        f"I've created a simple visualization and uploaded the song to YouTube with the title: "
        f"\"{video_title}\"\n\n"
        f"You can view it here: {video_url}\n\n"
        f"The video has been optimized with tags related to AI, collaboration, and music. "
        f"I'll monitor the comments and engagement metrics and can provide feedback on how viewers respond to the song."
    )
    
    try:
        message_id = client.send_message(
            thread_id=thread_id,
            content=analysis,
            mentions=[yona_agent_id]
        )
        logger.info(f"Simulated YouTube agent response sent with message ID: {message_id}")
        return message_id
    except Exception as e:
        logger.error(f"Failed to send simulated YouTube agent response: {str(e)}")
        return None

def monitor_conversation(client, thread_id, yona_agent_id, youtube_agent_id, args):
    """Monitor the conversation between agents and simulate responses if needed."""
    logger.info(f"Monitoring conversation in thread: {thread_id}")
    
    start_time = time.time()
    last_message_count = 0
    yona_responded = False
    youtube_responded_to_song = False
    
    while time.time() - start_time < args.max_wait_time:
        try:
            # Get messages in the thread
            messages = client.get_thread_messages(thread_id)
            
            if not messages:
                logger.warning("No messages found in the thread")
                time.sleep(args.poll_interval)
                continue
            
            # If we have new messages, print them
            if len(messages) > last_message_count:
                for i in range(last_message_count, len(messages)):
                    msg = messages[i]
                    sender = msg.get('sender_id', 'Unknown')
                    content = msg.get('content', 'No content')
                    logger.info(f"New message from {sender}: {content[:100]}...")
                
                last_message_count = len(messages)
            
            # Check if Yona has responded to the initial request
            if not yona_responded and len(messages) >= 2:
                for msg in messages[1:]:  # Skip the first message (our request)
                    if msg.get('sender_id') == yona_agent_id:
                        logger.info("Yona has responded with a song")
                        yona_responded = True
                        break
            
            # Check if YouTube agent has responded to Yona's song
            if yona_responded and not youtube_responded_to_song and len(messages) >= 3:
                for msg in messages[2:]:  # Skip the first two messages
                    if msg.get('sender_id') == youtube_agent_id:
                        logger.info("YouTube agent has responded to the song")
                        youtube_responded_to_song = True
                        break
            
            # If we're simulating responses and agents haven't responded, do it
            if args.simulate_responses:
                if not yona_responded and len(messages) == 1:
                    logger.info("Simulating Yona's response as it hasn't responded yet")
                    simulate_yona_response(client, thread_id, yona_agent_id, youtube_agent_id)
                    yona_responded = True
                    time.sleep(2)  # Brief pause between simulated messages
                
                if yona_responded and not youtube_responded_to_song and len(messages) == 2:
                    logger.info("Simulating YouTube agent's response as it hasn't responded yet")
                    simulate_youtube_response(client, thread_id, youtube_agent_id, yona_agent_id)
                    youtube_responded_to_song = True
            
            # If both agents have responded, we're done
            if yona_responded and youtube_responded_to_song:
                logger.info("Workflow completed successfully!")
                return True
            
            # Wait before polling again
            time.sleep(args.poll_interval)
            
        except Exception as e:
            logger.error(f"Error monitoring conversation: {str(e)}")
            time.sleep(args.poll_interval)
    
    logger.warning(f"Workflow did not complete within {args.max_wait_time} seconds")
    return False

def main():
    """Main function to run the workflow simulation."""
    args = parse_args()
    
    logger.info("Starting agent workflow simulation")
    logger.info(f"Yona Agent ID: {args.yona_agent_id}")
    logger.info(f"YouTube Agent ID: {args.youtube_agent_id}")
    
    # Create Coral client
    client = CoralClient(
        session_id=args.session_id,
        server_url=args.server_url,
        use_devmode=True
    )
    
    # Create thread
    thread_id = create_workflow_thread(client, args.yona_agent_id, args.youtube_agent_id)
    if not thread_id:
        logger.error("Simulation failed: Could not create thread")
        return
    
    # YouTube agent requests a song
    message_id = request_song(client, thread_id, args.youtube_agent_id, args.yona_agent_id)
    if not message_id:
        logger.error("Simulation failed: Could not send song request")
        return
    
    # Monitor the conversation and simulate responses if needed
    workflow_completed = monitor_conversation(
        client, thread_id, args.yona_agent_id, args.youtube_agent_id, args
    )
    
    if workflow_completed:
        logger.info("Simulation SUCCESSFUL: Full workflow completed")
    else:
        logger.warning("Simulation INCOMPLETE: Workflow did not complete in the allotted time")
    
    logger.info("Simulation ended")

if __name__ == "__main__":
    main()
