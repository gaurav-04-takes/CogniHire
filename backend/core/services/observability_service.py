import os
from backend.config.settings import settings
from backend.core.services.logging_service import logger

class ObservabilityService:
    @staticmethod
    def setup():
        """
        Initializes LangSmith tracing based on environment settings.
        """
        if settings.LANGCHAIN_TRACING_V2.lower() == "true":
            if not settings.LANGCHAIN_API_KEY:
                logger.warning("LangSmith tracing enabled but LANGCHAIN_API_KEY is missing. Tracing will fail.")
            
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY or ""
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
            logger.info("LangSmith tracing enabled.")
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            logger.info("LangSmith tracing disabled.")

# Call setup immediately on import if needed, or explicitly from main.py
ObservabilityService.setup()
