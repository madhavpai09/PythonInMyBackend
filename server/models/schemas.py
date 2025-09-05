from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

class RideRequestDB(BaseModel):
    id: Optional[int] = None
    user_id: str
    source_location: str
    dest_location: str
    created_at: Optional[datetime] = None
    status: str = "pending"
    is_active: bool = True
