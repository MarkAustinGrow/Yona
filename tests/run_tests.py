"""
Test runner for the Yona project.
"""
import unittest
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from test_agent import TestYonaAgent
from test_music_api import TestMusicAPI
from test_db import TestDatabase

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestYonaAgent))
    test_suite.addTest(unittest.makeSuite(TestMusicAPI))
    test_suite.addTest(unittest.makeSuite(TestDatabase))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful()) 