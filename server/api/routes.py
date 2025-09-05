from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from ..models.database import get_db
from ..models.schemas import (
    PingRequest, PingResponse, 
    RideRequestCreate, RideRequestResponse
)
from ..services.ride_service import RideService
from ..config import settings

router = APIRouter()

@router.post("/ping", response_model=PingResponse)
async def ping_endpoint(request: PingRequest):
    """Test endpoint for ping-pong functionality"""
    if request.data == "ping":
        return PingResponse(message="pong", status="success")
    else:
        # BUG: Should handle this more gracefully
        raise HTTPException(status_code=400, detail="Expected 'ping' but got something else")

@router.post("/ride-request", response_model=RideRequestResponse)
async def submit_ride_request(
    ride_request: RideRequestCreate,
    db: Session = Depends(get_db)
):
    """Submit a new ride request"""
    try:
        ride_service = RideService(db)
        
        # If PostgreSQL is not available, just print the data
        if not settings.USE_POSTGRES:
            print("=" * 50)
            print("We will store this data in Postgres now")
            print(f"User ID: {ride_request.user_id}")
            print(f"Source Location: {ride_request.source_location}")
            print(f"Destination Location: {ride_request.dest_location}")
            print("=" * 50)
            
            # Return a mock response
            return RideRequestResponse(
                id=999,  # Mock ID
                user_id=ride_request.user_id,
                source_location=ride_request.source_location,
                dest_location=ride_request.dest_location,
                created_at=datetime.utcnow(),
                status="pending"
            )
        
        # Store in actual database
        db_ride = ride_service.create_ride_request(ride_request)
        return RideRequestResponse.from_orm(db_ride)
        
    except Exception as e:
        print(f"Error creating ride request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create ride request")

@router.get("/ride-requests", response_model=List[RideRequestResponse])
async def get_ride_requests(
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Get all ride requests or filter by user_id"""
    try:
        ride_service = RideService(db)
        rides = ride_service.get_ride_requests(user_id=user_id)
        return [RideRequestResponse.from_orm(ride) for ride in rides]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch ride requests")

@router.get("/ride-requests/{ride_id}", response_model=RideRequestResponse)
async def get_ride_request(
    ride_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific ride request"""
    ride_service = RideService(db)
    ride = ride_service.get_ride_request(ride_id)
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride request not found")
    
    return RideRequestResponse.from_orm(ride)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "mini-uber-server",
        "database": "postgres" if settings.USE_POSTGRES else "sqlite"
    }