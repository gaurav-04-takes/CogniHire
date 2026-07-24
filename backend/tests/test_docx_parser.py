import pytest
from unittest.mock import MagicMock, patch
from backend.core.domain.document import Document
from backend.infrastructure.parsers.docx_parser import DOCXDocumentParser

@pytest.fixture
def parser():
    return DOCXDocumentParser()

@patch('backend.infrastructure.parsers.docx_parser.DocxDocument')
def test_docx_parser_success(mock_docx_document, parser):
    # Setup mock
    mock_doc = MagicMock()
    
    mock_p1 = MagicMock()
    mock_p1.text = "Heading 1"
    mock_p1.style.name = "Heading 1"
    
    mock_p2 = MagicMock()
    mock_p2.text = "Bullet point"
    mock_p2.style.name = "List Bullet"
    
    mock_p3 = MagicMock()
    mock_p3.text = "Normal text  with spaces"
    mock_p3.style.name = "Normal"
    
    mock_doc.paragraphs = [mock_p1, mock_p2, mock_p3]
    mock_docx_document.return_value = mock_doc
    
    doc = Document(id="test1", filename="test.docx", content=b"fake-docx-bytes", file_type="docx")
    parsed_doc = parser.parse(doc)
    
    assert "Heading 1" in parsed_doc.text_content
    assert "- Bullet point" in parsed_doc.text_content
    assert "Normal text with spaces" in parsed_doc.text_content
    
    mock_docx_document.assert_called_once()

@patch('backend.infrastructure.parsers.docx_parser.DocxDocument')
def test_docx_parser_failure(mock_docx_document, parser):
    mock_docx_document.side_effect = Exception("Corrupt DOCX")
    
    doc = Document(id="test2", filename="bad.docx", content=b"bad", file_type="docx")
    with pytest.raises(RuntimeError, match="Failed to parse DOCX document"):
        parser.parse(doc)
