#!/bin/bash
# Script to fix the requirements.txt file on the server

# Create a backup of the original file
cp requirements.txt requirements.txt.bak

# Remove the langchain-coral dependency
sed -i '/langchain-coral/d' requirements.txt

# Add a comment explaining why it's removed
echo "# langchain-coral is not available on PyPI, using local implementation instead" >> requirements.txt

echo "Fixed requirements.txt file. You can now rebuild the Docker containers:"
echo "docker-compose build --no-cache"
echo "docker-compose up -d"
