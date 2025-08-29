#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
  lsof -i:"$1" >/dev/null 2>&1
}

# Function to display error and exit
error_exit() {
  echo -e "${RED}ERROR: $1${NC}" >&2
  exit 1
}

# Function to display info
info() {
  echo -e "${BLUE}INFO: $1${NC}"
}

# Function to display success
success() {
  echo -e "${GREEN}SUCCESS: $1${NC}"
}

# Function to display warning
warning() {
  echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check for required dependencies
info "Checking dependencies..."
if ! command_exists python3; then
  error_exit "Python 3 is not installed. Please install Python 3 and try again."
fi

if ! command_exists pip3; then
  error_exit "pip3 is not installed. Please install pip3 and try again."
fi

if ! command_exists node; then
  error_exit "Node.js is not installed. Please install Node.js and try again."
fi

if ! command_exists npm; then
  error_exit "npm is not installed. Please install npm and try again."
fi

# Check if .env file exists
if [ ! -f "/workspace/ARBEngine/.env" ]; then
  warning ".env file not found. Creating from example..."
  cp /workspace/ARBEngine/.env.example /workspace/ARBEngine/.env
  warning "Please update the .env file with your OKX API credentials."
fi

# Check if ports are already in use
if port_in_use 8000; then
  warning "Port 8000 is already in use. The API server may not start correctly."
fi

# Install Python dependencies if needed
info "Checking Python dependencies..."
pip3 install -r /workspace/ARBEngine/requirements.txt

# Install Node.js dependencies if needed
info "Checking Node.js dependencies..."
cd /workspace/ARBEngine/Dashboard
npm install

# Create logs directory
mkdir -p /workspace/ARBEngine/logs

# Start the OKX API server in the background
info "Starting OKX API server..."
cd /workspace/ARBEngine
python3 -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --log-level info > logs/api_server.log 2>&1 &
API_PID=$!

# Wait for API server to start
sleep 3
if ! ps -p $API_PID > /dev/null; then
  error_exit "API server failed to start. Check logs/api_server.log for details."
fi

# Check if API server is responding
info "Checking API server..."
for i in {1..5}; do
  if curl -s http://localhost:8000/ > /dev/null; then
    success "API server is running at http://localhost:8000/"
    break
  fi
  
  if [ $i -eq 5 ]; then
    warning "API server may not be responding. Continuing anyway..."
  fi
  
  sleep 1
done

# Start the Dashboard in development mode
info "Starting Dashboard..."
cd /workspace/ARBEngine/Dashboard
npm start &
DASHBOARD_PID=$!

# Wait for Dashboard to start
sleep 3
if ! ps -p $DASHBOARD_PID > /dev/null; then
  warning "Dashboard may have failed to start. Continuing anyway..."
fi

# Display success message
success "ARBEngine is now running!"
success "API server: http://localhost:8000/"
success "Dashboard: Check the Expo QR code above"
success "Press Ctrl+C to stop all services"

# Function to clean up on exit
cleanup() {
  info "Shutting down services..."
  kill $API_PID 2>/dev/null
  kill $DASHBOARD_PID 2>/dev/null
  success "Services stopped. Goodbye!"
  exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT

# Wait for user to press Ctrl+C
wait $DASHBOARD_PID
cleanup