@echo off
echo Starting Yona Continuous Feedback Processor...
echo Press Ctrl+C to stop the processor
cd /d "%~dp0"
python src/continuous_feedback_processor.py
pause
