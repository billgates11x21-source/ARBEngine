#!/bin/bash

# Start the OKX API server in the background
echo "Starting OKX API server..."
cd /workspace/ARBEngine
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API server to start
sleep 2
echo "API server started with PID: $API_PID"

# Start the Dashboard in development mode
echo "Starting Dashboard..."
cd /workspace/ARBEngine/Dashboard
npm start

# If the dashboard is closed, also kill the API server
kill $API_PID