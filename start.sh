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

# Detect if running on Replit
if [ -n "$REPL_ID" ]; then
  info "Running on Replit environment"
  IS_REPLIT=true
  # Set the port to the Replit assigned port
  PORT=${REPL_SLUG:-8000}
  DASHBOARD_PORT=3000
else
  info "Running on local environment"
  IS_REPLIT=false
  PORT=8000
  DASHBOARD_PORT=19000
fi

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check for required dependencies
info "Checking dependencies..."
if ! command_exists python3; then
  warning "Python 3 is not installed. Attempting to install..."
  if [ "$IS_REPLIT" = true ]; then
    # On Replit, Python should already be available
    error_exit "Python 3 should be available on Replit. Please check your replit.nix file."
  else
    # Try to install Python on local environment
    apt-get update && apt-get install -y python3 python3-pip
  fi
fi

if ! command_exists pip3; then
  warning "pip3 is not installed. Attempting to install..."
  if [ "$IS_REPLIT" = true ]; then
    # On Replit, pip should already be available
    error_exit "pip3 should be available on Replit. Please check your replit.nix file."
  else
    # Try to install pip on local environment
    apt-get update && apt-get install -y python3-pip
  fi
fi

if ! command_exists node; then
  warning "Node.js is not installed. Attempting to install..."
  if [ "$IS_REPLIT" = true ]; then
    # On Replit, Node.js should already be available
    error_exit "Node.js should be available on Replit. Please check your replit.nix file."
  else
    # Try to install Node.js on local environment
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
    apt-get install -y nodejs
  fi
fi

if ! command_exists npm; then
  warning "npm is not installed. Attempting to install..."
  if [ "$IS_REPLIT" = true ]; then
    # On Replit, npm should already be available
    error_exit "npm should be available on Replit. Please check your replit.nix file."
  else
    # Try to install npm on local environment
    apt-get install -y npm
  fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
  warning ".env file not found. Creating from example..."
  if [ -f ".env.example" ]; then
    cp .env.example .env
    warning "Please update the .env file with your OKX API credentials."
  else
    # Create a basic .env file
    cat > .env << EOL
# === OKX API ===
OKX_API_KEY=e67dcc1c-ef28-4b14-aca3-08e3c516f2a5
OKX_API_SECRET=09682969064CADC393B1B6CE381893F9
OKX_API_PASSPHRASE=1Okx_Rage
OKX_API_NAME=Okx_Rage
OKX_PERMISSIONS=Read/Withdraw/Trade
OKX_IP=0.0.0.0/0,2406:da1c:136::/48,2406:da1c:136:5d00:b7c:de0c:fcbf:5e0c,52.64.36.145

# === Aggregators ===
ONEINCH_API_KEY=gBPPFE7U2al7K9WxaQxt04tDNPwGXBsH
ZEROX_API_KEY=101023a6-8d79-4133-9abf-c7c5369e7008

# === RPC Example ===
RPC_1=https://mainnet.infura.io/v3/YOUR_KEY

# === Wallet ===
PRIVATE_KEY=0x_your_private_key
EOL
    warning "Created default .env file with provided OKX API credentials."
  fi
fi

# Check if ports are already in use
if port_in_use $PORT; then
  warning "Port $PORT is already in use. The API server may not start correctly."
fi

# Install Python dependencies
info "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create logs directory
mkdir -p logs

# Start the OKX API server in the background
info "Starting OKX API server on port $PORT..."
if [ "$IS_REPLIT" = true ]; then
  # On Replit, we need to bind to 0.0.0.0 and use the Replit port
  python3 -m uvicorn src.api.server:app --host 0.0.0.0 --port $PORT --log-level info > logs/api_server.log 2>&1 &
else
  # On local environment
  python3 -m uvicorn src.api.server:app --host 0.0.0.0 --port $PORT --log-level info > logs/api_server.log 2>&1 &
fi
API_PID=$!

# Wait for API server to start
sleep 3
if ! ps -p $API_PID > /dev/null; then
  error_exit "API server failed to start. Check logs/api_server.log for details."
fi

# Check if API server is responding
info "Checking API server..."
for i in {1..5}; do
  if curl -s http://localhost:$PORT/ > /dev/null; then
    success "API server is running at http://localhost:$PORT/"
    break
  fi
  
  if [ $i -eq 5 ]; then
    warning "API server may not be responding. Continuing anyway..."
  fi
  
  sleep 1
done

# If running on Replit, we need to expose the port
if [ "$IS_REPLIT" = true ]; then
  info "Running on Replit - API server is accessible at https://$REPL_SLUG.$REPL_OWNER.repl.co"
  
  # Install Dashboard dependencies
  info "Installing Dashboard dependencies..."
  cd Dashboard
  npm install
  
  # Build the Dashboard for production
  info "Building Dashboard for production..."
  npm run build
  
  # Serve the Dashboard using a simple HTTP server
  info "Starting Dashboard server..."
  npx serve -s build -l $DASHBOARD_PORT > ../logs/dashboard.log 2>&1 &
  DASHBOARD_PID=$!
  
  # Wait for Dashboard to start
  sleep 3
  if ! ps -p $DASHBOARD_PID > /dev/null; then
    warning "Dashboard may have failed to start. Check logs/dashboard.log for details."
  else
    success "Dashboard is running at https://$REPL_SLUG.$REPL_OWNER.repl.co"
  fi
  
  # Keep the script running to keep the Replit instance alive
  info "ARBEngine is now running on Replit!"
  info "API server: https://$REPL_SLUG.$REPL_OWNER.repl.co"
  info "Press Ctrl+C to stop all services"
  
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
  
  # Keep the script running
  while true; do
    sleep 60
    # Check if processes are still running
    if ! ps -p $API_PID > /dev/null; then
      warning "API server process died. Restarting..."
      python3 -m uvicorn src.api.server:app --host 0.0.0.0 --port $PORT --log-level info > logs/api_server.log 2>&1 &
      API_PID=$!
    fi
    
    if ! ps -p $DASHBOARD_PID > /dev/null; then
      warning "Dashboard process died. Restarting..."
      cd Dashboard
      npx serve -s build -l $DASHBOARD_PORT > ../logs/dashboard.log 2>&1 &
      DASHBOARD_PID=$!
      cd ..
    fi
  done
else
  # On local environment, start the Dashboard in development mode
  info "Starting Dashboard in development mode..."
  cd Dashboard
  npm start &
  DASHBOARD_PID=$!
  
  # Wait for Dashboard to start
  sleep 3
  if ! ps -p $DASHBOARD_PID > /dev/null; then
    warning "Dashboard may have failed to start. Continuing anyway..."
  fi
  
  # Display success message
  success "ARBEngine is now running!"
  success "API server: http://localhost:$PORT/"
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
fi