import pytest
from unittest.mock import MagicMock, patch
from backend.core.domain.document import Document
from backend.infrastructure.parsers.pdf_parser import PDFDocumentParser

@pytest.fixture
def parser():
    return PDFDocumentParser()

@patch('backend.infrastructure.parsers.pdf_parser.fitz.open')
def test_pdf_parser_success(mock_fitz_open, parser):
    # Setup mock
    mock_doc = MagicMock()
    mock_doc.page_count = 2
    
    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "Page 1 Content   with   spaces"
    
    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "Page 2 \n\n\n\nContent"
    
    mock_doc.load_page.side_effect = [mock_page1, mock_page2]
    mock_fitz_open.return_value = mock_doc
    
    # Execute
    doc = Document(id="test1", filename="test.pdf", content=b"fake-pdf-bytes", file_type="pdf")
    parsed_doc = parser.parse(doc)
    
    # Assert
    assert parsed_doc.metadata["num_pages"] == 2
    assert "Page 1 Content with spaces" in parsed_doc.text_content
    assert "Page 2 \n\nContent" in parsed_doc.text_content
    mock_fitz_open.assert_called_once_with(stream=b"fake-pdf-bytes", filetype="pdf")
    mock_doc.close.assert_called_once()

@patch('backend.infrastructure.parsers.pdf_parser.fitz.open')
def test_pdf_parser_failure(mock_fitz_open, parser):
    mock_fitz_open.side_effect = Exception("Corrupt PDF")
    
    doc = Document(id="test2", filename="bad.pdf", content=b"bad", file_type="pdf")
    with pytest.raises(RuntimeError, match="Failed to parse PDF document"):
        parser.parse(doc)
