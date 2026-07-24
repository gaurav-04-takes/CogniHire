import json
import os
from typing import Dict, Any

class PromptManager:
    def __init__(self, prompts_file: str = "backend/prompts/prompts.json"):
        self.prompts_file = prompts_file
        self.prompts: Dict[str, Any] = {}
        self._load_prompts()

    def _load_prompts(self):
        if not os.path.exists(self.prompts_file):
            raise FileNotFoundError(f"Prompts file not found at {self.prompts_file}")
        with open(self.prompts_file, 'r', encoding='utf-8') as f:
            self.prompts = json.load(f)

    def get_prompt(self, prompt_key: str, **kwargs) -> str:
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
        prompt_data = self.prompts.get(prompt_key)
        if not prompt_data:
            raise ValueError(f"Prompt '{prompt_key}' not found.")
        return prompt_data.get("version", "unknown")
