# Mini-Uber Project

A simple ride-sharing application with FastAPI server and client APIs.

## Team Members
- J Madhav Pai
- 

## Features
- Submit ride requests with user_id, source_location, and dest_location
- PostgreSQL database integration (with SQLite fallback)
- RESTful API design
- Client API that forwards requests to server
- Health check endpoints
- Comprehensive error handling

## API Endpoints

### Server (Port 8000)
- `POST /api/v1/ride-request` - Submit ride request
- `GET /api/v1/ride-requests` - Get all ride requests
- `GET /api/v1/ride-requests/{id}` - Get specific ride request
- `POST /api/v1/ping` - Test connectivity
- `GET /api/v1/health` - Health check

### Client (Port 8001)
- `POST /submit-ride` - Submit ride request (call this from Postman)
- `GET /rides` - Get rides
- `GET /rides/{id}` - Get specific ride
- `GET /ping` - Test server connectivity

Demo Commands for testing
Terminal 1: Start server
-cd server && python working_server.py

Terminal 2: Start client
-cd client && python working_client.py

Terminal 3: Test functionality
-curl -X POST "http://127.0.0.1:8001/submit-ride" \\
     -H "Content-Type: application/json" \\
     -d '{"user_id":"prof_demo","source_location":"Campus","dest_location":"City"}'
