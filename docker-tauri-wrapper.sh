#!/bin/bash

# Universal Docker-to-Tauri wrapper
# Usage: ./docker-tauri-wrapper.sh <docker-image> <host-port> <container-port>
# Example: ./docker-tauri-wrapper.sh nginx:alpine 8080 80

set -e

DOCKER_IMAGE="${1:-nginx:alpine}"
HOST_PORT="${2:-8080}"
CONTAINER_PORT="${3:-80}"
CONTAINER_NAME="tauri-app-$(date +%s)"

echo "🚀 Starting Docker container as Tauri app..."
echo "Docker Image: $DOCKER_IMAGE"
echo "Host Port: $HOST_PORT"
echo "Container Port: $CONTAINER_PORT"

# Stop any existing containers on this port
docker ps --filter "expose=$HOST_PORT" -q | xargs -r docker stop

# Start new container
CONTAINER_ID=$(docker run -d -p $HOST_PORT:$CONTAINER_PORT --name $CONTAINER_NAME $DOCKER_IMAGE)
echo "✅ Container started: $CONTAINER_ID"

# Update Tauri config dynamically
cat > src-tauri/tauri.conf.json << EOF
{
  "\$schema": "../node_modules/@tauri-apps/cli/schema.json",
  "build": {
    "beforeBuildCommand": "",
    "beforeDevCommand": "",
    "frontendDist": "../app",
    "devUrl": "http://localhost:$HOST_PORT"
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "createUpdaterArtifacts": false,
    "publisher": "Your Name",
    "copyright": "Copyright (c) 2025",
    "category": "DeveloperTool",
    "shortDescription": "Docker App in Tauri",
    "longDescription": "Running $DOCKER_IMAGE as desktop application"
  },
  "productName": "Docker App - $(echo $DOCKER_IMAGE | cut -d':' -f1)",
  "version": "1.0.0",
  "identifier": "com.docker.$(echo $DOCKER_IMAGE | sed 's/[^a-zA-Z0-9]//g')",
  "plugins": {},
  "app": {
    "windows": [
      {
        "title": "Docker App - $DOCKER_IMAGE",
        "width": 1200,
        "height": 800,
        "minWidth": 600,
        "minHeight": 400,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": null
    }
  }
}
EOF

echo "✅ Tauri config updated for http://localhost:$HOST_PORT"

# Wait for service to be ready
echo "⏳ Waiting for service to start..."
timeout 30 bash -c "until curl -s http://localhost:$HOST_PORT > /dev/null; do sleep 1; done" || {
    echo "⚠️  Service might not be ready yet, but continuing..."
}

# Launch Tauri in dev mode
echo "🚀 Launching Tauri app..."
cd src-tauri
source ~/.cargo/env 2>/dev/null || true

# Try to run Tauri
if command -v tauri >/dev/null 2>&1; then
    echo "Using Tauri CLI..."
    tauri dev
elif command -v cargo >/dev/null 2>&1; then
    echo "Using Cargo..."
    cargo tauri dev
else
    echo "❌ Neither Tauri CLI nor Cargo found. Please install Rust and Tauri CLI first."
    exit 1
fi

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    echo "✅ Cleanup complete"
}

trap cleanup EXIT
