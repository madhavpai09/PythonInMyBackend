import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://miniuber_user:miniuber_pass@localhost:5432/miniuber_db")
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
    USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

settings = Settings()

# Database setup
if settings.USE_POSTGRES:
    engine = create_engine(settings.DATABASE_URL)
else:
    # Fallback to SQLite for development
    engine = create_engine("sqlite:///./miniuber.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class RideRequest(Base):
    __tablename__ = "ride_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    source_location = Column(String, nullable=False)
    dest_location = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    is_active = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class PingRequest(BaseModel):
    data: str

class PingResponse(BaseModel):
    message: str
    status: str

class RideRequestCreate(BaseModel):
    user_id: str
    source_location: str
    dest_location: str

class RideRequestResponse(BaseModel):
    id: int
    user_id: str
    source_location: str
    dest_location: str
    created_at: datetime
    status: str
    
    class Config:
        from_attributes = True

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Service Layer
class RideService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_ride_request(self, ride_data: RideRequestCreate) -> RideRequest:
        """Create a new ride request"""
        try:
            db_ride = RideRequest(
                user_id=ride_data.user_id,
                source_location=ride_data.source_location,
                dest_location=ride_data.dest_location
            )
            self.db.add(db_ride)
            self.db.commit()
            self.db.refresh(db_ride)
            return db_ride
        except Exception as e:
            self.db.rollback()
            # BUG: Not handling database connection errors properly
            raise e
    
    def get_ride_requests(self, user_id: Optional[str] = None) -> List[RideRequest]:
        """Get ride requests, optionally filtered by user_id"""
        query = self.db.query(RideRequest).filter(RideRequest.is_active == True)
        if user_id:
            query = query.filter(RideRequest.user_id == user_id)
        return query.all()
    
    def get_ride_request(self, ride_id: int) -> Optional[RideRequest]:
        """Get a specific ride request by ID"""
        return self.db.query(RideRequest).filter(
            RideRequest.id == ride_id,
            RideRequest.is_active == True
        ).first()

# FastAPI App
app = FastAPI(
    title="Mini-Uber Server API",
    description="Server API for Mini-Uber ride sharing application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.post("/api/v1/ping", response_model=PingResponse)
async def ping_endpoint(request: PingRequest):
    """Test endpoint for ping-pong functionality"""
    if request.data == "ping":
        return PingResponse(message="pong", status="success")
    else:
        # BUG: Should handle this more gracefully
        raise HTTPException(status_code=400, detail="Expected 'ping' but got something else")

@app.post("/api/v1/ride-request", response_model=RideRequestResponse)
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

@app.get("/api/v1/ride-requests", response_model=List[RideRequestResponse])
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

@app.get("/api/v1/ride-requests/{ride_id}", response_model=RideRequestResponse)
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

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "mini-uber-server",
        "database": "postgres" if settings.USE_POSTGRES else "sqlite"
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to Mini-Uber Server API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚗 Starting Mini-Uber Server...")
    print(f"Server will run on: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(f"API Documentation: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs")
    print(f"Database mode: {'PostgreSQL' if settings.USE_POSTGRES else 'SQLite (fallback)'}")
    
    uvicorn.run(
        app, 
        host=settings.SERVER_HOST, 
        port=settings.SERVER_PORT, 
        reload=True
    )