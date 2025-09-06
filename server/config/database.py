import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'mini_uber'),
                user=os.getenv('DB_USER', 'uber_user'),
                password=os.getenv('DB_PASSWORD', 'your_password'),
                port=os.getenv('DB_PORT', 5432),
                cursor_factory=RealDictCursor  # Returns dict-like results
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    
    def execute_single(self, query, params=None):
        """Execute a SELECT query and return single result"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT query and return the inserted record"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                conn.commit()
                return result
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE/DELETE query and return affected rows count"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                affected_rows = cursor.rowcount
                conn.commit()
                return affected_rows
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("All database connections closed")

# Create a global database instance
db = DatabaseConnection()

# Convenience functions
def get_db():
    """Get the database instance"""
    return db

def init_database():
    """Initialize database tables"""
    create_tables_query = """
    -- Users table (drivers and riders)
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('rider', 'driver')),
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Drivers table (additional driver info)
    CREATE TABLE IF NOT EXISTS drivers (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        license_number VARCHAR(50) UNIQUE NOT NULL,
        vehicle_make VARCHAR(50),
        vehicle_model VARCHAR(50),
        vehicle_year INTEGER,
        vehicle_plate VARCHAR(20),
        is_available BOOLEAN DEFAULT false,
        current_lat DECIMAL(10,8),
        current_lng DECIMAL(11,8),
        rating DECIMAL(3,2) DEFAULT 5.0,
        total_trips INTEGER DEFAULT 0
    );

    -- Rides table
    CREATE TABLE IF NOT EXISTS rides (
        id SERIAL PRIMARY KEY,
        rider_id INTEGER REFERENCES users(id),
        driver_id INTEGER REFERENCES users(id),
        pickup_address TEXT NOT NULL,
        pickup_lat DECIMAL(10,8) NOT NULL,
        pickup_lng DECIMAL(11,8) NOT NULL,
        destination_address TEXT NOT NULL,
        destination_lat DECIMAL(10,8) NOT NULL,
        destination_lng DECIMAL(11,8) NOT NULL,
        status VARCHAR(20) DEFAULT 'requested' CHECK (status IN ('requested', 'accepted', 'in_progress', 'completed', 'cancelled')),
        fare DECIMAL(10,2),
        distance_km DECIMAL(8,2),
        estimated_duration INTEGER,
        requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        accepted_at TIMESTAMP,
        started_at TIMESTAMP,
        completed_at TIMESTAMP
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_drivers_available ON drivers(is_available);
    CREATE INDEX IF NOT EXISTS idx_rides_status ON rides(status);
    CREATE INDEX IF NOT EXISTS idx_rides_rider ON rides(rider_id);
    CREATE INDEX IF NOT EXISTS idx_rides_driver ON rides(driver_id);
    """
    
    try:
        db.execute_update(create_tables_query)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        raise