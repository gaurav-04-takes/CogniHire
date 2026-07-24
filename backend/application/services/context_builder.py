from typing import List, Tuple
from backend.core.domain.chunk import Chunk
from backend.core.domain.chat import Citation

class ContextBuilder:
    def build_context(self, chunks: List[Chunk]) -> Tuple[str, List[Citation]]:
        """
        Formats top reranked chunks into structured LLM context and extracts citations.
        Preserves document, page, section, and chunk references.
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
            
        context_string = "\n---\n".join(context_parts)
        return context_string, citations
