from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base  # Import Base from database.py

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
    
    status = Column(String, default="requested")  # requested, accepted, completed, cancelled
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
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id='{self.user_id}', name='{self.name}')>"