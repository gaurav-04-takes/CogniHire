from backend.core.interfaces.retriever import IRetriever
from backend.application.dto.retrieval import RetrieveRequest, RetrieveResponse, RetrievedChunk

class RetrieveRelevantChunksUseCase:
    def __init__(self, retriever: IRetriever):
        self.retriever = retriever

    def execute(self, request: RetrieveRequest) -> RetrieveResponse:
        """
        Executes a semantic search to retrieve relevant chunks from a specific collection,
        applying any provided metadata filters.
        """
        chunks = self.retriever.retrieve(
            query=request.query,
            collection_name=request.collection_name,
            filters=request.filters,
            top_k=request.top_k
        )
        
        response_chunks = []
        for chunk in chunks:
            response_chunks.append(RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_type=chunk.doc_type.value,
                section_type=chunk.section_type,
                chunk_index=chunk.metadata.get("chunk_index", 0),
                score=chunk.score,
                text=chunk.text
            ))
            
        return RetrieveResponse(
            query=request.query,
            results=response_chunks
        )
