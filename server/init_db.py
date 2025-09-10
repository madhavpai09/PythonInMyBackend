import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import create_tables, test_connection, engine
from models.model import RideRequest, User

def main():
    print("🚀 Initializing Mini Uber Database...")
    
    # Test connection first
    print("📡 Testing database connection...")
    if not test_connection():
        print("❌ Failed to connect to database. Please check your configuration.")
        return False
    
    print("✅ Database connection successful!")
    
    # Create tables
    print("📋 Creating database tables...")
    try:
        create_tables()
        print("✅ Tables created successfully!")
        
        # Verify tables were created
        inspector = engine.inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Created tables: {tables}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Database initialization completed successfully!")
    else:
        print("💥 Database initialization failed!")
        sys.exit(1)