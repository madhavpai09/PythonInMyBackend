import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, test_connection
from models.model import RideRequest, User

def test_database_operations():
    print("🧪 Testing database operations...")
    
    # Test connection
    if not test_connection():
        print("❌ Database connection failed!")
        return False
    
    db = SessionLocal()
    
    try:
        # Test 1: Create a user
        print("👤 Testing User creation...")
        test_user = User(
            user_id="test_user_123",
            name="John Doe",
            phone="+1234567890",
            email="john@example.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Created user: {test_user}")
        
        # Test 2: Create a ride request
        print("🚗 Testing RideRequest creation...")
        test_ride = RideRequest(
            user_id="test_user_123",
            source_location="123 Main St",
            dest_location="456 Oak Ave",
            source_latitude=40.7128,
            source_longitude=-74.0060,
            dest_latitude=40.7589,
            dest_longitude=-73.9851,
            estimated_fare=15.50,
            estimated_duration=20,
            distance=5.2
        )
        db.add(test_ride)
        db.commit()
        db.refresh(test_ride)
        print(f"✅ Created ride request: {test_ride}")
        
        # Test 3: Query data
        print("🔍 Testing data retrieval...")
        users = db.query(User).all()
        rides = db.query(RideRequest).all()
        print(f"📊 Found {len(users)} users and {len(rides)} ride requests")
        
        # Test 4: Update data
        print("✏️ Testing data update...")
        test_ride.status = "completed"
        db.commit()
        print(f"✅ Updated ride status to: {test_ride.status}")
        
        # Test 5: Delete test data
        print("🧹 Cleaning up test data...")
        db.delete(test_ride)
        db.delete(test_user)
        db.commit()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("🚀 Starting Mini Uber Database Tests...")
    
    success = test_database_operations()
    
    if success:
        print("🎉 All database tests passed!")
    else:
        print("💥 Database tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()