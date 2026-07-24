import logging
import json
import sys
from datetime import datetime
from backend.config.settings import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
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
    @staticmethod
    def setup_logger(name: str) -> logging.Logger:
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
