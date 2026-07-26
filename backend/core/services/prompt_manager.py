"""
Prompt management service.

Architectural layer:
    Application services.

Purpose:
    Loads and provides formatting for externalized LLM prompts. 
    Prompts remain outside use cases to allow tuning without code changes.

Data flow:
    Reads from a JSON file and provides formatted prompt strings to
    application use cases.

Key dependencies:
    - JSON prompts file.

Side effects:
    - Reads from the filesystem on initialization.

Related modules:
    None.
"""
import json
import os
from typing import Dict, Any

class PromptManager:
    """
    Service for loading and managing prompt templates.
    """
    def __init__(self, prompts_file: str = "backend/prompts/prompts.json"):
        self.prompts_file = prompts_file
        self.prompts: Dict[str, Any] = {}
        self._load_prompts()

    def _load_prompts(self):
        """Load the prompts from the JSON file into memory."""
        if not os.path.exists(self.prompts_file):
            raise FileNotFoundError(f"Prompts file not found at {self.prompts_file}")
        with open(self.prompts_file, 'r', encoding='utf-8') as f:
            self.prompts = json.load(f)

    def get_prompt(self, prompt_key: str, **kwargs) -> str:
        """
        Retrieve and format a prompt by its key.

        Args:
            prompt_key: The identifier for the prompt in the JSON file.
            **kwargs: Variables required to format the prompt template.

        Returns:
            The fully formatted prompt string.
            
        Raises:
            ValueError: If the prompt key is missing, or if required variables
                for formatting are not provided.
        """
        prompt_data = self.prompts.get(prompt_key)
        if not prompt_data:
            raise ValueError(f"Prompt '{prompt_key}' not found.")
        
        system_prompt = prompt_data.get("system_prompt", "")
        if kwargs:
            try:
                system_prompt = system_prompt.format(**kwargs)
            except KeyError as e:
                raise ValueError(f"Missing variable {e} for prompt '{prompt_key}'")
        return system_prompt

    def get_version(self, prompt_key: str) -> str:
        """
        Retrieve the version of a given prompt.

        Args:
            prompt_key: The identifier for the prompt.

        Returns:
            The version string, or 'unknown' if not specified.
            
        Raises:
            ValueError: If the prompt key is not found.
        """
        prompt_data = self.prompts.get(prompt_key)
        if not prompt_data:
            raise ValueError(f"Prompt '{prompt_key}' not found.")
        return prompt_data.get("version", "unknown")
