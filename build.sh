#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to display error
error() {
  echo -e "${RED}ERROR: $1${NC}"
}

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Install Python dependencies
info "Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Dashboard dependencies
info "Installing Dashboard dependencies..."
cd Dashboard
npm install

# Build the Dashboard for production
info "Building Dashboard for production..."
npm run build

success "Build completed successfully!"
success "You can now run the application using './start.sh'"