from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI(title="Mini-Uber Client")

class RideRequest(BaseModel):
    user_id: str
    source_location: str
    dest_location: str

@app.post("/submit-ride")
async def submit_ride(ride_request: RideRequest):
    try:
        # Forward to server
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/ride-request",
            json={
                "user_id": ride_request.user_id,
                "source_location": ride_request.source_location,
                "dest_location": ride_request.dest_location
            },
            timeout=10
        )
        response.raise_for_status()
        
        return {
            "status": "success",
            "message": "Ride request submitted",
            "data": response.json()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "Mini-Uber Client is Running!"}

if __name__ == "__main__":
    print("🚗 Starting Mini-Uber Client...")
    print("Client will be available at: http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)