from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, create_tables, test_connection
from models.model import RideRequest, User
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Create FastAPI instance
app = FastAPI(title="Mini Uber API", version="1.0.0")

# Pydantic models for API
class RideRequestCreate(BaseModel):
    user_id: str
    source_location: str
    dest_location: str
    source_latitude: Optional[float] = None
    source_longitude: Optional[float] = None
    dest_latitude: Optional[float] = None
    dest_longitude: Optional[float] = None

class UserCreate(BaseModel):
    user_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting Mini Uber API...")
    
    if not test_connection():
        print("❌ Failed to connect to database!")
        raise Exception("Database connection failed")
    
    print("✅ Database connected successfully")
    create_tables()
    print("📋 Database tables ready")

@app.get("/")
async def root():
    return {"message": "Mini Uber API is running!", "status": "healthy"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Simple database query to check connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get a user by user_id"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/rides/")
async def create_ride_request(ride: RideRequestCreate, db: Session = Depends(get_db)):
    """Create a new ride request"""
    db_ride = RideRequest(**ride.dict())
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    return db_ride

@app.get("/rides/")
async def get_rides(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all ride requests"""
    rides = db.query(RideRequest).offset(skip).limit(limit).all()
    return rides

@app.get("/rides/{ride_id}")
async def get_ride(ride_id: int, db: Session = Depends(get_db)):
    """Get a ride request by ID"""
    ride = db.query(RideRequest).filter(RideRequest.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)