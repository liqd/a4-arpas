#!/bin/bash

echo "Updating arpas-arc package..."

# Save current directory
ORIGINAL_DIR=$(pwd)

# Function to cleanup on exit
cleanup() {
    cd "$ORIGINAL_DIR"
}

# Set trap to ensure we return to original directory
trap cleanup EXIT

# Navigate to arpas-arc and build
echo "Building arpas-arc..."
cd "../arpas-arc" || { echo "Error: Could not navigate to arpas-arc directory"; exit 1; }

npm run build
if [ $? -ne 0 ]; then
    echo "Error: arpas-arc build failed"
    exit 1
fi

# Navigate back to arpas directory
cd "$ORIGINAL_DIR" || { echo "Error: Could not return to arpas directory"; exit 1; }

# Force reinstall the local package
echo "Reinstalling arpas-arc package..."
npm install arpas-arc@file:../arpas-arc --force

if [ $? -ne 0 ]; then
    echo "Error: npm install failed"
    exit 1
fi

echo "arpas-arc package updated successfully!"
