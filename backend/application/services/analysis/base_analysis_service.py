"""
Base Analysis Service.

Architectural layer:
    Application (Service).

Purpose:
    Provides common JSON parsing utility methods for the various LLM-driven
    analysis services. Ensures that markdown code blocks returned by the LLM
    are properly stripped before attempting Pydantic model validation.

Data flow:
    Accepts a raw text string (presumably containing JSON) and a Pydantic Model
    type. Returns an instantiated Pydantic model.

Key dependencies:
    - pydantic

Related modules:
    - backend.application.services.analysis.*
"""
import json
from pydantic import BaseModel
from typing import Type, TypeVar

T = TypeVar('T', bound=BaseModel)

class BaseAnalysisService:
    """
    Parent class for LLM structural output parsing.
    """
    def _parse_json(self, text: str, model: Type[T]) -> T:
        """
        Cleans markdown wrappers from LLM responses and attempts to parse into a Pydantic model.
        
        Args:
            text: Raw string response from the LLM.
            model: The Pydantic model class to validate against.
            
        Returns:
            An instance of the specified Pydantic model.
            
        Raises:
            ValueError: If the JSON is invalid or fails Pydantic schema validation.
        """
        try:
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return model.model_validate_json(text.strip())
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {e}\nRaw output: {text}")
