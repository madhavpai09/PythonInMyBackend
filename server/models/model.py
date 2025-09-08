from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base

class RideRequest(Base):
    """Model for ride requests in your Velo app"""
    __tablename__ = "ride_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    source_location = Column(String, nullable=False)
    dest_location = Column(String, nullable=False)
    
    # Additional useful fields
    source_latitude = Column(Float, nullable=True)
    source_longitude = Column(Float, nullable=True)
    dest_latitude = Column(Float, nullable=True)
    dest_longitude = Column(Float, nullable=True)
    
    status = Column(String, default="requested")  # requested, accepted, in_progress, completed, cancelled
    estimated_fare = Column(Float, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    distance = Column(Float, nullable=True)  # in kilometers
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RideRequest(id={self.id}, user_id='{self.user_id}', status='{self.status}')>"

class User(Base):
    """User model for your Velo app"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)  # External user ID
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # User preferences
    preferred_vehicle_type = Column(String, default="any")  # car, bike, auto
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(user_id='{self.user_id}', name='{self.name}')>"

# schemas.py - Pydantic schemas for your Velo app
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RideRequestCreate(BaseModel):
    """Schema for creating ride requests"""
    user_id: str = Field(..., description="User identifier")
    source_location: str = Field(..., description="Pickup location")
    dest_location: str = Field(..., description="Destination location")
    source_latitude: Optional[float] = None
    source_longitude: Optional[float] = None
    dest_latitude: Optional[float] = None
    dest_longitude: Optional[float] = None

class RideRequestResponse(BaseModel):
    """Schema for ride request responses"""
    id: int
    user_id: str
    source_location: str
    dest_location: str
    source_latitude: Optional[float] = None
    source_longitude: Optional[float] = None
    dest_latitude: Optional[float] = None
    dest_longitude: Optional[float] = None
    status: str
    estimated_fare: Optional[float] = None
    estimated_duration: Optional[int] = None
    distance: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """Schema for creating users"""
    user_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_vehicle_type: Optional[str] = "any"

class UserResponse(BaseModel):
    """Schema for user responses"""
    id: int
    user_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_vehicle_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True