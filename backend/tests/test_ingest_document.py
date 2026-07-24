import pytest
from unittest.mock import MagicMock
from backend.core.domain.document import Document, DocumentType, ParsedDocument
from backend.core.domain.chunk import Chunk
from backend.application.use_cases.ingest_document import IngestDocumentUseCase

@pytest.fixture
def mock_dependencies():
    return {
        "pdf_parser": MagicMock(),
        "docx_parser": MagicMock(),
        "classifier": MagicMock(),
        "section_parser": MagicMock(),
        "chunker": MagicMock(),
        "metadata_extractor": MagicMock(),
        "embedder": MagicMock(),
        "index_repository": MagicMock()
    }

@pytest.fixture
def pipeline(mock_dependencies):
    return IngestDocumentUseCase(**mock_dependencies)

def test_execute_pdf_success(pipeline, mock_dependencies):
    doc = Document(id="doc1", filename="test.pdf", content=b"pdf", file_type="pdf")
    
    parsed_doc = ParsedDocument(document_id="doc1", doc_type=DocumentType.UNKNOWN, text_content="pdf text")
    mock_dependencies["pdf_parser"].parse.return_value = parsed_doc
    
    class_res = MagicMock()
    class_res.document_type = DocumentType.RESUME
    class_res.dict.return_value = {"confidence": 0.9}
    mock_dependencies["classifier"].classify.return_value = class_res
    
    mock_dependencies["metadata_extractor"].extract.return_value = {"name": "Test"}
    mock_dependencies["section_parser"].parse_sections.return_value = []
    
    chunk = Chunk(id="c1", document_id="doc1", doc_type=DocumentType.RESUME, text="chunk text")
    mock_dependencies["chunker"].chunk_document.return_value = [chunk]
    
    mock_dependencies["embedder"].embed_documents.return_value = [[0.1, 0.2]]
    
    num_chunks, doc_type, class_dict = pipeline.execute(doc)
    
    assert num_chunks == 1
    assert doc_type == DocumentType.RESUME
    assert class_dict == {"confidence": 0.9}
    
    mock_dependencies["pdf_parser"].parse.assert_called_once_with(doc)
    mock_dependencies["classifier"].classify.assert_called_once_with("pdf text")
    mock_dependencies["index_repository"].index_chunks.assert_called_once()
    assert chunk.metadata["embedding"] == [0.1, 0.2]

def test_execute_docx_success(pipeline, mock_dependencies):
    doc = Document(id="doc2", filename="test.docx", content=b"docx", file_type="docx")
    
    parsed_doc = ParsedDocument(document_id="doc2", doc_type=DocumentType.UNKNOWN, text_content="docx text")
    mock_dependencies["docx_parser"].parse.return_value = parsed_doc
    
    class_res = MagicMock()
    class_res.document_type = DocumentType.JOB_DESCRIPTION
    class_res.dict.return_value = {}
    mock_dependencies["classifier"].classify.return_value = class_res
    
    mock_dependencies["chunker"].chunk_document.return_value = []
    
    num_chunks, doc_type, _ = pipeline.execute(doc)
    
    assert num_chunks == 0
    assert doc_type == DocumentType.JOB_DESCRIPTION
    mock_dependencies["docx_parser"].parse.assert_called_once_with(doc)

def test_execute_unknown_type_early_exit(pipeline, mock_dependencies):
    doc = Document(id="doc3", filename="test.pdf", content=b"pdf", file_type="pdf")
    parsed_doc = ParsedDocument(document_id="doc3", doc_type=DocumentType.UNKNOWN, text_content="text")
    mock_dependencies["pdf_parser"].parse.return_value = parsed_doc
    
    class_res = MagicMock()
    class_res.document_type = DocumentType.UNKNOWN
    class_res.dict.return_value = {}
    mock_dependencies["classifier"].classify.return_value = class_res
    
    num_chunks, doc_type, _ = pipeline.execute(doc)
    
    assert num_chunks == 0
    assert doc_type == DocumentType.UNKNOWN
    mock_dependencies["metadata_extractor"].extract.assert_not_called()

def test_execute_override(pipeline, mock_dependencies):
    doc = Document(id="doc4", filename="test.pdf", content=b"pdf", file_type="pdf", doc_type_override=DocumentType.JOB_DESCRIPTION)
    parsed_doc = ParsedDocument(document_id="doc4", doc_type=DocumentType.UNKNOWN, text_content="text")
    mock_dependencies["pdf_parser"].parse.return_value = parsed_doc
    
    class_res = MagicMock()
    class_res.document_type = DocumentType.RESUME
    class_res.dict.return_value = {}
    mock_dependencies["classifier"].classify.return_value = class_res
    
    mock_dependencies["chunker"].chunk_document.return_value = []
    
    num_chunks, doc_type, _ = pipeline.execute(doc)
    
    assert doc_type == DocumentType.JOB_DESCRIPTION

def test_execute_unsupported_file_type(pipeline, mock_dependencies):
    doc = Document(id="doc5", filename="test.txt", content=b"txt", file_type="txt")
    with pytest.raises(ValueError, match="Unsupported file type"):
        pipeline.execute(doc)
