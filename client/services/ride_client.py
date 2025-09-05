import requests
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class RideClient:
    def __init__(self, server_url: str = None):
        self.server_url = server_url or os.getenv("SERVER_URL", "http://localhost:8000")
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def submit_ride_request(self, user_id: str, source_location: str, dest_location: str) -> Dict[str, Any]:
        """Submit a ride request to the server"""
        url = f"{self.server_url}/api/v1/ride-request"
        payload = {
            "user_id": user_id,
            "source_location": source_location,
            "dest_location": dest_location
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            # BUG: Should retry or handle connection errors better
            raise Exception("Could not connect to server. Is the server running?")
        except requests.exceptions.Timeout:
            raise Exception("Server request timed out")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Server returned error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def get_ride_requests(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get ride requests from server"""
        url = f"{self.server_url}/api/v1/ride-requests"
        params = {"user_id": user_id} if user_id else {}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get ride requests: {str(e)}")
    
    def get_ride_request(self, ride_id: int) -> Dict[str, Any]:
        """Get specific ride request"""
        url = f"{self.server_url}/api/v1/ride-requests/{ride_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get ride request: {str(e)}")
    
    def ping_server(self) -> Dict[str, Any]:
        """Test server connectivity"""
        url = f"{self.server_url}/api/v1/ping"
        payload = {"data": "ping"}
        
        try:
            response = self.session.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "failed", "error": str(e)}