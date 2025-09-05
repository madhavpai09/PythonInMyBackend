import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uvicorn
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Ride Client Service
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

# Initialize ride client
ride_client = RideClient()

# Pydantic Models
class RideRequestInput(BaseModel):
    user_id: str
    source_location: str
    dest_location: str

# FastAPI Client App
app = FastAPI(
    title="Mini-Uber Client API",
    description="Client API that communicates with Mini-Uber Server",
    version="1.0.0"
)

@app.post("/submit-ride")
async def submit_ride_request(ride_request: RideRequestInput):
    """
    Client API endpoint to submit ride request
    This will be called from Postman/curl and forwards to server
    """
    try:
        result = ride_client.submit_ride_request(
            user_id=ride_request.user_id,
            source_location=ride_request.source_location,
            dest_location=ride_request.dest_location
        )
        return {
            "status": "success",
            "message": "Ride request submitted successfully",
            "data": result
        }
    except Exception as e:
        # BUG: Generic exception handling without specific error types
        raise HTTPException(status_code=500, detail=f"Failed to submit ride request: {str(e)}")

@app.get("/rides")
async def get_rides(user_id: str = None):
    """Get all rides or filter by user_id"""
    try:
        result = ride_client.get_ride_requests(user_id=user_id)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rides: {str(e)}")

@app.get("/rides/{ride_id}")
async def get_ride(ride_id: int):
    """Get specific ride by ID"""
    try:
        result = ride_client.get_ride_request(ride_id)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ride: {str(e)}")

@app.get("/ping")
async def ping_server():
    """Test server connectivity"""
    try:
        result = ride_client.ping_server()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server ping failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Mini-Uber Client API",
        "version": "1.0.0",
        "usage": "Use /submit-ride endpoint to submit ride requests",
        "docs": "/docs"
    }

if __name__ == "__main__":
    print("🚗 Starting Mini-Uber Client API...")
    print("Client API will be available at: http://localhost:8001")
    print("API Documentation: http://localhost:8001/docs")
    print("Make sure the server is running at: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)