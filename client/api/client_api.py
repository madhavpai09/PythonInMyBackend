from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ride_client import RideClient

app = FastAPI(
    title="Mini-Uber Client API",
    description="Client API that communicates with Mini-Uber Server",
    version="1.0.0"
)

# Initialize ride client
ride_client = RideClient()

class RideRequestInput(BaseModel):
    user_id: str
    source_location: str
    dest_location: str

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)