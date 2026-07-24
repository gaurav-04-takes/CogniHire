import pytest
from unittest.mock import AsyncMock, patch
from backend.infrastructure.llm.gemini_provider import GeminiProvider
from backend.config.settings import settings

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake_key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-test")
    return settings

@pytest.mark.asyncio
@patch("backend.infrastructure.llm.gemini_provider.ChatGoogleGenerativeAI")
async def test_gemini_generate(mock_chat_class, mock_settings):
    # Setup mock
    mock_llm_instance = AsyncMock()
    mock_llm_instance.ainvoke.return_value.content = "Test response"
    mock_chat_class.return_value = mock_llm_instance
    
    # Init provider
    provider = GeminiProvider()
    
    # Execute
    response = await provider.generate("Hello", system_prompt="You are a helpful assistant")
    
    # Assert
    assert response == "Test response"
    mock_llm_instance.ainvoke.assert_called_once()
    
    # Check messages structure passed to ainvoke
    messages = mock_llm_instance.ainvoke.call_args[0][0]
    assert len(messages) == 2
    assert messages[0].content == "You are a helpful assistant"
    assert messages[1].content == "Hello"

@pytest.mark.asyncio
@patch("backend.infrastructure.llm.gemini_provider.ChatGoogleGenerativeAI")
async def test_gemini_stream(mock_chat_class, mock_settings):
    # Setup mock
    mock_llm_instance = AsyncMock()
    
    # Mock astream generator
    async def mock_astream(*args, **kwargs):
        class Chunk:
            def __init__(self, content):
                self.content = content
        yield Chunk("Test ")
        yield Chunk("response")
        
    mock_llm_instance.astream = mock_astream
    mock_chat_class.return_value = mock_llm_instance
    
    provider = GeminiProvider()
    
    chunks = []
    async for chunk in provider.stream("Hello"):
        chunks.append(chunk)
        
    assert chunks == ["Test ", "response"]
