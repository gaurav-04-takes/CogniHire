"""
Context Building Service.

Architectural layer:
    Application (Service).

Purpose:
    Transforms raw Chunk domain objects retrieved from the vector store into
    a formatted string suitable for LLM injection. Also constructs formal
    Citation objects mapping back to source documents.

Data flow:
    Accepts Chunks, parses their metadata, and returns a single concatenated
    string alongside a list of Citation objects.

Key dependencies:
    - backend.core.domain.chunk
    - backend.core.domain.chat

Related modules:
    - backend.application.use_cases.chat_pipeline
"""
from typing import List, Tuple
from backend.core.domain.chunk import Chunk
from backend.core.domain.chat import Citation

class ContextBuilder:
    """
    Formats retrieved chunks into LLM context and extracts structured citations.
    """
    def build_context(self, chunks: List[Chunk]) -> Tuple[str, List[Citation]]:
        """
        Formats top reranked chunks into structured LLM context and extracts citations.
        Preserves document, page, section, and chunk references.
        
        Args:
            chunks: A list of retrieved and reranked Chunk objects.
            
        Returns:
            A tuple containing:
                - The formatted string to be injected into the LLM system prompt.
                - A list of Citation objects representing the origins of the context.
        """
        context_parts = []
        citations = []
        
        for chunk in chunks:
            # Extract metadata safely
            page = chunk.metadata.get('page')
            chunk_index = chunk.metadata.get('chunk_index', 0)
            
            # Create citation object
            citation = Citation(
                document_id=chunk.document_id,
                document_type=chunk.doc_type.value if hasattr(chunk.doc_type, 'value') else str(chunk.doc_type),
                section_type=chunk.section_type or "Unknown",
                chunk_index=chunk_index,
                page=page
            )
            citations.append(citation)
            
            # Format context part
            citation_str = citation.format()
            context_parts.append(f"Source: {citation_str}\nContent:\n{chunk.text}\n")
            
            # Use three hyphens as a delimiter for the LLM to differentiate chunks
        context_string = "\n---\n".join(context_parts)
        return context_string, citations
