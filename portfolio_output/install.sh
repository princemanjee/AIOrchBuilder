#!/bin/bash
echo "🚀 Starting AIOrch Automated Installer..."
echo "📦 Checking dependencies..."
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Error: Docker is not installed. Please install it first."
  exit 1
fi
echo "✅ Docker found."
echo "🏗️ Building the application swarm..."
docker-compose up --build -d
echo "✨ Success! Your app is running at http://localhost:3000"
