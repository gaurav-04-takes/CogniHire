import json
from pydantic import BaseModel
from typing import Type, TypeVar

T = TypeVar('T', bound=BaseModel)

class BaseAnalysisService:
    def _parse_json(self, text: str, model: Type[T]) -> T:
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
