"""
Logging utilities for the Yona application.

This module provides custom logging handlers and utilities for the Yona application,
including a Supabase log handler that sends logs to a Supabase table.
"""
import logging
import json
from typing import Optional

class SupabaseLogHandler(logging.Handler):
    """
    Custom logging handler that sends logs to a Supabase table.
    """
    def __init__(self, supabase_client, container=None):
        super().__init__()
        self.supabase = supabase_client
        self.container = container
        
    def emit(self, record):
        try:
            # Extract exception info if present
            exc_info = None
            if record.exc_info:
                exc_info = self.formatter.formatException(record.exc_info)
            
            # Convert record created time to ISO format
            from datetime import datetime
            timestamp = datetime.fromtimestamp(record.created).isoformat()
            
            # Format the log message
            log_entry = {
                "timestamp": timestamp,  # Add timestamp field
                "level": record.levelname,
                "source": record.name,
                "message": self.format(record),
                "details": {
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "pathname": record.pathname,
                    "exc_info": exc_info,
                    "container": self.container  # Add container identifier
                }
            }
            
            # Insert into Supabase
            self.supabase.client.table("yona_logs").insert(log_entry).execute()
        except Exception:
            # Don't let logging errors crash the application
            self.handleError(record)
