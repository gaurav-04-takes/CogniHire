import requests
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, data: Optional[Any] = None, files: Optional[Any] = None) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}{endpoint}", json=json, data=data, files=files)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str) -> Dict[str, Any]:
        response = requests.delete(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()

    def stream_post(self, endpoint: str, json: Dict[str, Any]):
        response = requests.post(f"{self.base_url}{endpoint}", json=json, stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=None, decode_unicode=True)

api_client = APIClient()
