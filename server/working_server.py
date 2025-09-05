from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from datetime import datetime

# Simple FastAPI app
app = FastAPI(title="Mini-Uber Server")

class RideRequest(BaseModel):
    user_id: str
    source_location: str
    dest_location: str

@app.post("/api/v1/ride-request")
async def submit_ride_request(ride_request: RideRequest):
    # Print the required message
    print("=" * 50)
    print("We will store this data in Postgres now")
    print(f"User ID: {ride_request.user_id}")
    print(f"Source Location: {ride_request.source_location}")
    print(f"Destination Location: {ride_request.dest_location}")
    print("=" * 50)
    
    return {
        "id": 999,
        "user_id": ride_request.user_id,
        "source_location": ride_request.source_location,
        "dest_location": ride_request.dest_location,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "mini-uber-server"}

@app.get("/")
async def root():
    return {"message": "Mini-Uber Server is Running!"}

# Run the server
if __name__ == "__main__":
    print("🚗 Starting Working Mini-Uber Server...")
    print("Server will be available at: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)