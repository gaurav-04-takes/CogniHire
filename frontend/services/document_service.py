"""
Frontend Document Service.

Architectural layer:
    Frontend (Service Abstraction).

Purpose:
    Abstracts API calls related to document ingestion, status tracking, and deletion.
"""
from typing import List, Dict, Any
from frontend.services.api_client import api_client

class DocumentService:
    """
    Provides static methods to interact with the backend `/documents` endpoints.
    """
    
    @staticmethod
    def get_documents() -> List[Dict[str, Any]]:
        """
        Retrieves a list of all uploaded documents.
        """
        response = api_client.get("/documents")
        return response.get("documents", [])

    @staticmethod
    def get_document(doc_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information for a specific document.
        """
        return api_client.get(f"/documents/{doc_id}")

    @staticmethod
    def get_status(doc_id: str) -> Dict[str, Any]:
        """
        Retrieves the current ingestion pipeline status for a specific document.
        """
        return api_client.get(f"/documents/{doc_id}/status")

    @staticmethod
    def upload_document(file_content: bytes, filename: str, doc_type: str = "auto") -> Dict[str, Any]:
        """
        Uploads a new document file via multipart/form-data.
        """
        files = {"file": (filename, file_content)}
        data = {"document_type": doc_type}
        return api_client.post("/documents/upload", files=files, data=data)

    @staticmethod
    def delete_document(doc_id: str) -> Dict[str, Any]:
        """
        Deletes a document from the system and its associated vector embeddings.
        """
        return api_client.delete(f"/documents/{doc_id}")

    @staticmethod
    def reindex_document(doc_id: str) -> Dict[str, Any]:
        """
        Forces a reindex of an existing document. (Endpoint must be implemented in backend).
        """
        return api_client.post(f"/documents/{doc_id}/reindex")
        
    @staticmethod
    def reclassify_document(doc_id: str, new_type: str) -> Dict[str, Any]:
        """
        Triggers reclassification and re-ingestion of a document with a forced type.
        """
        return api_client.post(f"/documents/{doc_id}/reclassify", json={"document_type": new_type})
