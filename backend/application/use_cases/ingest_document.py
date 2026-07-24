from typing import Optional, Tuple
from backend.core.domain.document import Document, DocumentType
from backend.core.interfaces.parser import IDocumentParser
from backend.core.interfaces.classifier import IDocumentClassifier
from backend.core.interfaces.section_parser import ISectionParser
from backend.core.interfaces.embedder import IEmbedder
from backend.core.interfaces.index_repository import IIndexRepository
from backend.infrastructure.chunkers.section_chunker import SectionAwareChunker
from backend.infrastructure.parsers.metadata_extractor import MetadataExtractor

class IngestDocumentUseCase:
    def __init__(
        self,
        pdf_parser: IDocumentParser,
        docx_parser: IDocumentParser,
        classifier: IDocumentClassifier,
        section_parser: ISectionParser,
        chunker: SectionAwareChunker,
        metadata_extractor: MetadataExtractor,
        embedder: IEmbedder,
        index_repository: IIndexRepository
    ):
        self.pdf_parser = pdf_parser
        self.docx_parser = docx_parser
        self.classifier = classifier
        self.section_parser = section_parser
        self.chunker = chunker
        self.metadata_extractor = metadata_extractor
        self.embedder = embedder
        self.index_repository = index_repository

    def execute(self, document: Document) -> Tuple[int, DocumentType, Optional[dict]]:
        """
        Executes the ingestion pipeline.
        Returns the number of chunks indexed, the detected DocumentType, and classification details.
        """
        # 1. Parse raw text
        if document.file_type.lower() == 'pdf':
            parsed_doc = self.pdf_parser.parse(document)
        elif document.file_type.lower() in ['docx', 'doc']:
            parsed_doc = self.docx_parser.parse(document)
        else:
            raise ValueError(f"Unsupported file type: {document.file_type}")
            
        # 2. Classify Document Type
        classification_res = self.classifier.classify(parsed_doc.text_content)
        doc_type = classification_res.document_type
        
        # Apply manual override if provided
        if document.doc_type_override and document.doc_type_override != DocumentType.UNKNOWN:
            doc_type = document.doc_type_override
            
        parsed_doc.doc_type = doc_type
        
        # If it's UNKNOWN, we do not index yet. We wait for user input.
        if doc_type == DocumentType.UNKNOWN:
            return 0, doc_type, classification_res.dict()
        
        # 3. Extract Metadata
        metadata = self.metadata_extractor.extract(parsed_doc.text_content, doc_type)
        parsed_doc.metadata.update(metadata)
        
        # 4. Detect Sections
        sections = self.section_parser.parse_sections(parsed_doc.text_content, doc_type)
        parsed_doc.sections = sections
        
        # 5. Section-Aware Chunking
        chunks = self.chunker.chunk_document(parsed_doc)
        
        if not chunks:
            return 0, doc_type, classification_res.dict()
            
        # 6. Generate Embeddings
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_documents(chunk_texts)
        
        for chunk, emb in zip(chunks, embeddings):
            chunk.metadata["embedding"] = emb
            
        # 7. Index in ChromaDB
        collection_name = "documents" # Unify for unified retrieval
        self.index_repository.index_chunks(chunks, collection_name)
        
        return len(chunks), doc_type, classification_res.dict()
