import pytest
from backend.core.services.prompt_manager import PromptManager
import os
import tempfile
import json

def test_prompt_manager_loads_prompts():
    manager = PromptManager()
    assert manager.prompts is not None
    assert "match_score" in manager.prompts

def test_get_prompt():
    manager = PromptManager()
    prompt = manager.get_prompt("match_score")
    assert "You are an expert technical recruiter" in prompt
    assert "Skills" in prompt

def test_get_prompt_with_kwargs():
    # Write a temporary prompts.json
    temp_prompts = {
        "test_prompt": {
            "version": "1.0",
            "system_prompt": "Hello {name}, your score is {score}"
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(temp_prompts, f)
        temp_path = f.name
        
    try:
        manager = PromptManager(prompts_file=temp_path)
        prompt = manager.get_prompt("test_prompt", name="Alice", score="100")
        assert prompt == "Hello Alice, your score is 100"
    finally:
        os.unlink(temp_path)
