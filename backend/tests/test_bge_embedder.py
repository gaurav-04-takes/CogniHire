import pytest
from unittest.mock import MagicMock, patch
from backend.infrastructure.embedders.bge_embedder import BGEEmbeddingProvider

@patch('backend.infrastructure.embedders.bge_embedder.GoogleGenerativeAIEmbeddings')
def test_embed_documents_uncached(mock_google_embeddings):
    # Setup mock
    mock_model = MagicMock()
    mock_model.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
    mock_google_embeddings.return_value = mock_model
    
    provider = BGEEmbeddingProvider()
    
    texts = ["text1", "text2"]
    embeddings = provider.embed_documents(texts)
    
    assert len(embeddings) == 2
    assert embeddings[0] == [0.1, 0.2]
    assert embeddings[1] == [0.3, 0.4]
    mock_model.embed_documents.assert_called_once_with(["text1", "text2"])

@patch('backend.infrastructure.embedders.bge_embedder.GoogleGenerativeAIEmbeddings')
def test_embed_documents_cached(mock_google_embeddings):
    # Setup mock
    mock_model = MagicMock()
    mock_model.embed_documents.return_value = [[0.1, 0.2]]
    mock_google_embeddings.return_value = mock_model
    
    provider = BGEEmbeddingProvider()
    
    # First call caches it
    emb1 = provider.embed_documents(["text1"])
    
    # Reset mock to ensure it's not called again
    mock_model.embed_documents.reset_mock()
    
    # Second call should use cache
    emb2 = provider.embed_documents(["text1"])
    
    assert emb1 == emb2
    mock_model.embed_documents.assert_not_called()

@patch('backend.infrastructure.embedders.bge_embedder.GoogleGenerativeAIEmbeddings')
def test_embed_query(mock_google_embeddings):
    # Setup mock
    mock_model = MagicMock()
    mock_model.embed_query.return_value = [0.9, 0.8]
    mock_google_embeddings.return_value = mock_model
    
    provider = BGEEmbeddingProvider()
    
    embedding = provider.embed_query("query")
    
    assert embedding == [0.9, 0.8]
    mock_model.embed_query.assert_called_once_with("query")
