#!/usr/bin/env python3
"""
Improved Script to fix the Coral adapter's message handling.

This script modifies the YonaCoralAdapter class to improve message handling
and fix issues with mention detection. It checks if the fix has already been
applied and adds more logging to help diagnose issues.
"""

import logging
import argparse
import re
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("improved_fix_coral_adapter")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fix Coral adapter message handling")
    parser.add_argument("--file", default="src/coral_adapter.py", help="Path to coral_adapter.py")
    parser.add_argument("--backup", action="store_true", help="Create a backup of the original file")
    parser.add_argument("--force", action="store_true", help="Apply the fix even if it appears to be already applied")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def backup_file(file_path):
    """Create a backup of the file."""
    import shutil
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    return backup_path

def is_fix_already_applied(content):
    """Check if the fix has already been applied."""
    # Check for key indicators that the fix has been applied
    indicators = [
        "Check for mentions in various formats",
        "Check for @agent_id pattern in content",
        "Check for <@agent_id> pattern in content",
        "Check for \"yona\" in content"
    ]
    
    for indicator in indicators:
        if indicator in content:
            return True
    
    return False

def fix_default_message_handler(content):
    """Fix the _default_message_handler method to improve mention detection."""
    # Find the _default_message_handler method
    pattern = r'def _default_message_handler\(self, data\):.*?(?=\n    def|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        logger.error("Could not find _default_message_handler method")
        return content
    
    original_method = match.group(0)
    logger.info("Found _default_message_handler method")
    
    # Check if the fix has already been applied
    if is_fix_already_applied(original_method):
        logger.info("Fix appears to be already applied to _default_message_handler")
        return content
    
    # Create improved version of the method
    improved_method = """def _default_message_handler(self, data):
        \"\"\"
        Default handler for message events.
        
        Args:
            data: The message data.
        \"\"\"
        logger.info(f"Received message: {json.dumps(data, indent=2)}")
        
        try:
            # Check if this message mentions Yona
            content = data.get('content', '')
            thread_id = data.get('thread_id')
            sender_id = data.get('sender_id')
            
            # Check for mentions in various formats
            mentioned = False
            mention_type = None
            
            # Check if agent_id is in the mentions list
            if self.agent_id in data.get('mentions', []):
                mentioned = True
                mention_type = "mentions list"
                logger.info(f"Found mention in mentions list: {self.agent_id}")
            
            # Check for @agent_id pattern in content
            elif self.agent_id and f"@{self.agent_id}" in content:
                mentioned = True
                mention_type = "@mention"
                logger.info(f"Found @mention in content: @{self.agent_id}")
            
            # Check for <@agent_id> pattern in content (alternate format)
            elif self.agent_id and f"<@{self.agent_id}>" in content:
                mentioned = True
                mention_type = "<@mention>"
                logger.info(f"Found <@mention> in content: <@{self.agent_id}>")
                
            # Check for "yona" in content (case insensitive)
            elif "yona" in content.lower():
                mentioned = True
                mention_type = "name mention"
                logger.info(f"Found 'yona' in content")
            
            # If using a pending agent ID, check for any mention patterns
            elif self.agent_id == "pending":
                # Look for any @mention pattern
                mention_pattern = r'@(\\S+)'
                mentions = re.findall(mention_pattern, content)
                if mentions:
                    mentioned = True
                    mention_type = "pending @mention"
                    logger.info(f"Found mentions while agent_id is pending: {mentions}")
            
            if mentioned and thread_id and sender_id:
                logger.info(f"Received message mention from {sender_id} in thread {thread_id} (type: {mention_type})")
                
                try:
                    # Generate a song concept based on the prompt
                    logger.info(f"Generating song concept from prompt: {content}")
                    concept = self.yona_agent.generate_song_concept(content)
                    
                    # Generate lyrics based on the concept
                    logger.info(f"Generating lyrics for concept: {concept}")
                    lyrics = self.yona_agent.generate_lyrics(concept)
                    
                    # Create the song
                    logger.info(f"Creating song with title: {concept.get('title')}")
                    song_result = self.yona_agent.create_song(
                        title=concept.get('title'),
                        lyrics=lyrics,
                        style=concept.get('style_tags'),
                        negative_tags=concept.get('negative_tags'),
                        make_instrumental=concept.get('make_instrumental', False),
                        mv=concept.get('mv_type', 'sonic-v4'),
                        gpt_description_prompt=concept.get('description')
                    )
                    
                    # Prepare the response message
                    if song_result.get('status') == 'failed':
                        message = f"Sorry, I couldn't create a song based on your prompt. Error: {song_result.get('error')}"
                    else:
                        message = (f"Created song '{concept.get('title')}'\n"
                                  f"Audio: {song_result.get('audio_url')}\n"
                                  f"Lyrics:\n{lyrics}")
                    
                    # Send the response
                    logger.info(f"Sending response to thread {thread_id}")
                    self.send_message(thread_id, message, [sender_id])
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    # Send error message
                    error_message = f"Sorry, I encountered an error while creating your song: {str(e)}"
                    self.send_message(thread_id, error_message, [sender_id])
            else:
                if not mentioned:
                    logger.debug(f"Message does not mention Yona")
                elif not thread_id:
                    logger.warning(f"Message mentions Yona but is missing thread_id")
                elif not sender_id:
                    logger.warning(f"Message mentions Yona but is missing sender_id")
        except Exception as e:
            logger.error(f"Error in default message handler: {str(e)}")"""
    
    # Replace the method
    new_content = content.replace(original_method, improved_method)
    return new_content

def fix_coral_adapter(file_path, create_backup=False, force=False):
    """Fix the Coral adapter file."""
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the fix has already been applied
        if is_fix_already_applied(content) and not force:
            logger.info("Fix appears to be already applied to the file. Use --force to apply anyway.")
            return True
        
        # Create backup if requested
        if create_backup:
            backup_file(file_path)
        
        # Fix the _default_message_handler method
        new_content = fix_default_message_handler(content)
        
        # Check if the content was actually modified
        if new_content == content:
            logger.warning("No changes were made to the file")
            return True
        
        # Write the modified content back to the file
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        logger.info(f"Successfully updated {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error fixing Coral adapter: {str(e)}")
        return False

def main():
    """Main function."""
    args = parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Fixing Coral adapter in {args.file}")
    
    # Check if the file exists
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    success = fix_coral_adapter(args.file, args.backup, args.force)
    
    if success:
        logger.info("Coral adapter fixed successfully")
        logger.info("To apply the changes, restart the Yona container:")
        logger.info("  docker restart yona_yona-coral_1")
        return 0
    else:
        logger.error("Failed to fix Coral adapter")
        return 1

if __name__ == "__main__":
    sys.exit(main())
