"""
Application logging service.

Architectural layer:
    Application services.

Purpose:
    Provides a standardized JSON logging format and central logger setup
    for the entire application.

Data flow:
    Accepts log events from any part of the application and writes them to
    standard output in JSON format.

Key dependencies:
    - Python standard logging.

Side effects:
    - Writes to sys.stdout.

Related modules:
    - backend.config.settings
"""
import logging
import json
import sys
from datetime import datetime
from backend.config.settings import settings

class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs log records as JSON strings.
    """
    def format(self, record):
        """Format the LogRecord as a JSON string."""
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage()
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

class LoggingService:
    """
    Service responsible for configuring and providing loggers.
    """
    @staticmethod
    def setup_logger(name: str) -> logging.Logger:
        """
        Configure and return a named logger with JSON formatting.

        Args:
            name: The name of the logger to create or retrieve.

        Returns:
            A configured standard library Logger instance.
        """
        logger = logging.getLogger(name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
            
        logger.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        
        logger.addHandler(handler)
        logger.propagate = False
        return logger

# Create a central app logger
logger = LoggingService.setup_logger("cognihire")
