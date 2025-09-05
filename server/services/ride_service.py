from sqlalchemy.orm import Session
from ..models.database import RideRequest
from ..models.schemas import RideRequestCreate
from typing import List, Optional

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
            # This could crash if database is unavailable
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