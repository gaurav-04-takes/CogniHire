"""
FastAPI HTTP Client.

Architectural layer:
    Frontend (API Integration).

Purpose:
    Wraps the `requests` library to provide a standardized, reusable client for
    making HTTP requests to the FastAPI backend. Handles JSON parsing and error raising.
"""
import requests
from typing import Dict, Any, Optional

class APIClient:
    """
    Standardized HTTP client for backend communication.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Initializes the client with a target backend base URL.
        """
        self.base_url = base_url

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes an HTTP GET request and returns the parsed JSON response.
        """
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, data: Optional[Any] = None, files: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes an HTTP POST request and returns the parsed JSON response.
        """
        response = requests.post(f"{self.base_url}{endpoint}", json=json, data=data, files=files)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Executes an HTTP DELETE request and returns the parsed JSON response.
        """
        response = requests.delete(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()

    def stream_post(self, endpoint: str, json: Dict[str, Any]):
        """
        Executes an HTTP POST request optimized for Server-Sent Events (SSE) or streaming responses.
        Yields raw string chunks.
        """
        response = requests.post(f"{self.base_url}{endpoint}", json=json, stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=None, decode_unicode=True)

# Singleton instance for use across frontend services
api_client = APIClient()
